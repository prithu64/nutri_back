# main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.ocr_services import extract_text
from services.feature_builder import build_ml_features
from services.ml_classifier import predict_health_score

from pydantic import BaseModel
from services.ocr.postprocess import clean_tokens

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextPayload(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "NutriSnap Backend Running"}

@app.post("/extract-text")
async def extract_text_endpoint(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    # 1. OCR Stage
    result = extract_text(image_bytes)
    raw_text = result.get('cleaned', '')
    
    # 2. UX Stage: Pre-parse the raw text to generate a beautiful list for the frontend
    import re
    parsed = clean_tokens(raw_text)
    nutrition = parsed.get('nutrition_values', {})
    
    formatted_text = "--- PLEASE REVIEW AND CORRECT ---\n\n"
    
    keys = [
        ('energy', 'Energy', 'kcal'),
        ('protein', 'Protein', 'g'),
        ('total_fat', 'Total Fat', 'g'),
        ('saturated_fat', 'Saturated Fat', 'g'),
        ('carbohydrates', 'Carbohydrates', 'g'),
        ('sugars', 'Total Sugars', 'g'),
        ('sodium', 'Sodium', 'mg'),
        ('fiber', 'Fiber', 'g')
    ]
    
    for key, label, unit in keys:
        val = nutrition.get(key)
        if val:
            # Strip string units so we can format it perfectly for the Regex downstream
            num = re.sub(r'[^\d\.]', '', val)
            formatted_text += f"{label} {num} {unit}\n"
        else:
            formatted_text += f"{label} 0 {unit}    <--- MISSING: PLEASE FIX\n"
            
    formatted_text += "\n\n--- RAW SCAN DATA (For Reference) ---\n\n"
    formatted_text += raw_text

    return {
        "status": "success",
        "extracted_text": formatted_text
    }

@app.post("/analyze-text")
async def analyze_text_endpoint(payload: TextPayload):
    # Important: Only parse the data ABOVE the raw scan reference divider
    # to prevent the "Last-Match" logic from sniping messy raw data.
    clean_input = payload.text.split("--- RAW SCAN DATA")[0]
    
    result = clean_tokens(clean_input)
    nutrition_dict = result.get('nutrition_values', {})
    
    # 2. Feature Building Stage
    features = build_ml_features(nutrition_dict)
    
    # 3. ML Classification Stage
    health_assessment = predict_health_score(features)
    
    # 4. Generate Health Tips (WHO guidelines scaled to 100g)
    health_tips = []
    if features[1] > 20: # Total Fat
        health_tips.append({"text": f"Excessive total fat ({features[1]:.1f}g) - Exceeds optimal limits", "type": "negative"})
    if features[6] > 5:  # Saturated Fat
        health_tips.append({"text": f"High saturated fat ({features[6]:.1f}g) - Increases cardiovascular risk", "type": "negative"})
    if features[2] > 15: # Sugars
        health_tips.append({"text": f"High added sugars ({features[2]:.1f}g) - Monitor glucose impact", "type": "negative"})
    if features[3] > 600: # Sodium
        health_tips.append({"text": f"High sodium density ({features[3]:.1f}mg) - Exceeds FSSAI safe limits", "type": "negative"})
    if features[4] > 10: # Protein
        health_tips.append({"text": f"Excellent protein source ({features[4]:.1f}g per 100g)", "type": "positive"})
    if features[5] > 5:  # Fiber
        health_tips.append({"text": f"High in dietary fiber ({features[5]:.1f}g) - Supports digestion", "type": "positive"})
    if not health_tips:
        health_tips.append({"text": "Moderate nutritional profile with no extreme spikes.", "type": "neutral"})
        
    # 5. Call LLM for Dynamic Assessment
    from services.llm_service import generate_llm_assessment
    llm_assessment, llm_recommendation = generate_llm_assessment(health_assessment['grade'], features)
        
    return {
        "status": "success",
        "nutrition_values": nutrition_dict,
        "additives": result.get('additives', []),
        "health_tips": health_tips,
        "ml_features": {
            "energy_100g": features[0],
            "fat_100g": features[1],
            "sugars_100g": features[2],
            "sodium_100g": features[3],
            "protein_100g": features[4],
            "fiber_100g": features[5],
            "saturated_fat_100g": features[6],
            "carbohydrates_100g": features[7]
        },
        "health_score": health_assessment,
        "llm_assessment": llm_assessment,
        "llm_recommendation": llm_recommendation
    }
