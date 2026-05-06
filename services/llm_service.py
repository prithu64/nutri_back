# services/llm_service.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API Key loaded securely from .env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_llm_assessment(grade_str, features):
    """
    Calls OpenRouter LLM to generate dynamic clinical assessments based on XGBoost output.
    Uses a strict 8-second timeout to prevent the app from crashing during live presentations if Wi-Fi drops.
    """
    # Features array: [energy, fat, sugars, sodium, protein, fiber, sat_fat, carbs]
    macros = f"Energy: {features[0]:.1f}kcal, Fat: {features[1]:.1f}g, Sugar: {features[2]:.1f}g, Sodium: {features[3]:.1f}mg, Protein: {features[4]:.1f}g, Fiber: {features[5]:.1f}g"
    
    # Fallback text in case the free API fails or rate-limits during the presentation
    fallback_assessment = "Clinical analysis identifies specific nutritional imbalances that exceed standard safety thresholds. The XGBoost engine has flagged critical concerns in the nutrient profile."
    fallback_recommendation = "Immediate dietary caution is advised. Limit consumption of this product and prioritize whole, unprocessed alternatives to maintain metabolic health."
    
    try:
        print("Ping OpenRouter API...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "NutriSnap"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert Clinical Dietitian analyzing a food label for a consumer health app. The user provides macronutrients per 100g and an ML Health Grade (A-E). Your tone must be highly professional and scientifically accurate, but easily understandable for an average person. Do not use overly complex medical jargon. Output your response EXACTLY in this format, with no quotes, no headers, and no extra text:\n- [Bullet point explaining the specific health impact of the highest risk nutrient in clear terms]\n- [Bullet point explaining the broader metabolic or cardiovascular impact]\n|||\n[One sentence actionable dietary recommendation]"
                    },
                    {
                        "role": "user",
                        "content": f"Food Macros: {macros}. ML Grade: {grade_str}."
                    }
                ]
            },
            timeout=8  # 8 second timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print("LLM Response received successfully!")
            
            try:
                if '|||' in content:
                    parts = content.split('|||')
                    # Aggressively scrub any rogue quotation marks or asterisks
                    assessment = parts[0].strip().strip("'").strip('"').strip()
                    recommendation = parts[1].strip().strip("'").strip('"').strip()
                    
                    if not assessment:
                        assessment = fallback_assessment
                    return assessment, recommendation
                else:
                    return content.strip().strip("'").strip('"'), fallback_recommendation
            except Exception:
                return None, None
                
        else:
            print(f"LLM API Error: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"LLM API Exception: {e}")
        return None, None
