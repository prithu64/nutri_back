import re

def extract_float(value_str):
    if not value_str:
        return 0.0
    match = re.search(r'(\d+\.?\d*)', str(value_str))
    if match:
        return float(match.group(1))
    return 0.0

def build_ml_features(nutrition_dict):
    """
    Takes OCR nutrition output and converts it to the 8 features 
    expected by the ML model: [energy, fat, sugars, sodium, protein, fiber, sat_fat, carbs] per 100g.
    """
    
    # Extract raw numeric values
    energy_raw = extract_float(nutrition_dict.get('energy'))
    fat_raw = extract_float(nutrition_dict.get('total_fat'))
    sugars_raw = extract_float(nutrition_dict.get('sugars'))
    sodium_raw = extract_float(nutrition_dict.get('sodium'))
    protein_raw = extract_float(nutrition_dict.get('protein'))
    fiber_raw = extract_float(nutrition_dict.get('fiber'))
    sat_fat_raw = extract_float(nutrition_dict.get('saturated_fat'))
    carbs_raw = extract_float(nutrition_dict.get('carbohydrates'))
    
    serving_size_raw = extract_float(nutrition_dict.get('serving_size'))
    
    # Initialize variables
    energy_100 = energy_raw
    fat_100 = fat_raw
    sugars_100 = sugars_raw
    sodium_100 = sodium_raw
    protein_100 = protein_raw
    fiber_100 = fiber_raw
    sat_fat_100 = sat_fat_raw
    carbs_100 = carbs_raw
    
    # Scaling factor parsing
    # If serving size exists and > 0, we can accurately scale to 100g
    if serving_size_raw > 0:
        scale_factor = 100.0 / serving_size_raw
        
        # Test double scaling on fat/energy to see if we should scale everything
        test_fat = fat_raw * scale_factor
        test_energy = energy_raw * scale_factor
        
        # SANITY CHECK: Double scaling safeguard
        # If scaling causes macronutrients to exceed physical limits (e.g., > 100g per 100g)
        # Or if energy exceeds 900 kcal per 100g (the physical limit of pure fat).
        # It means the OCR grabbed the "Per 100g" column natively, so we shouldn't scale it!
        if test_fat <= 102 and test_energy <= 900:
            energy_100 = energy_raw * scale_factor
            fat_100 = fat_raw * scale_factor
            sugars_100 = sugars_raw * scale_factor
            sodium_100 = sodium_raw * scale_factor
            protein_100 = protein_raw * scale_factor
            fiber_100 = fiber_raw * scale_factor
            sat_fat_100 = sat_fat_raw * scale_factor
            carbs_100 = carbs_raw * scale_factor
            
    return [energy_100, fat_100, sugars_100, sodium_100, protein_100, fiber_100, sat_fat_100, carbs_100]
