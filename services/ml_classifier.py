import os
import joblib

# Locate the model correctly relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'nutrition_model.pkl')

model = None
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("ML model loaded successfully.")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}.")
except Exception as e:
    print(f"Error loading ML model: {e}")

CATEGORY_MAP = {
    4: 'A (Healthy)', 
    3: 'B (Healthy)', 
    2: 'C (Moderate)',  
    1: 'D (Unhealthy)', 
    0: 'E (Unhealthy)'
}

def predict_health_score(features):
    """
    Given an array of features [energy, fat, sugars, sodium] (per 100g),
    returns the predicted health grade.
    """
    if model is None:
        return {"grade": "Unknown (Model missing)", "confidence": 0.0}
    
    try:
        # scikit-learn predict methods expect a 2D array of samples
        pred = model.predict([features])[0]
        prob = model.predict_proba([features])[0]
        
        return {
            "grade": CATEGORY_MAP.get(pred, "Unknown"),
            "confidence": round(float(max(prob)), 4)
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return {"grade": "Calculation Error", "confidence": 0.0}
