# services/ocr/postprocess.py

import re

def clean_tokens(detections):
    """Simple and effective postprocessing"""
    
    # Convert list to string if needed
    if isinstance(detections, list):
        text = "\n".join(detections)
    else:
        text = detections
    
    # ============================================
    # STEP 1: Fix Common OCR Errors
    # ============================================
    corrections = {
        'kcall': 'kcal',
        'kaai': 'kcal',
        'm9': 'mg',
        'mgi': 'mg',
        'mgl': 'mg',
        '9g': 'g',
        'IINFORMATION': 'INFORMATION',
        'NFORMATION': 'INFORMATION',
        'Iake': 'Intake',
        'Oty': 'Qty',
        'Sering': 'Serving',
        'Qats': 'Oats',
        'Jeive': 'Serve',
        'Servet': 'Serve',
        'Servem': 'Serve',
        ']': '',
        '[': '',
    }
    
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    
    # ============================================
    # STEP 2: Fix Number Formatting
    # ============================================
    # Fix missing decimal: "2 35" -> "2.35"
    text = re.sub(r'(\d+)\s+(\d{2})(?=\s|g|mg|kcal|%)', r'\1.\2', text)
    
    # Fix merged numbers dropped spacing: "122.49" -> "12.2 4.9", "84.34" -> "8.4 3.4"
    # This happens when OCR drops the middle space and the first decimal point.
    text = re.sub(r'\b(\d+)(\d)\.(\d)(\d)\b', r'\1.\2 \3.\4', text)
    
    # Fix leading zeros: "08.04" -> "8.04"
    text = re.sub(r'\b0(\d+\.\d+)\b', r'\1', text)
    text = re.sub(r'\b0(\d+)\b', r'\1', text)
    
    # Fix 20 kcal -> 200 kcal (common OCR error)
    if '20 kcal' in text and '200' in text:
        text = text.replace('20 kcal', '200 kcal')
    
    # Clean extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # ============================================
    # STEP 3: Extract Nutrition Values
    # ============================================
    nutrition = {}
    
    # Global "9 to g" correction: OCR often reads "g" as "9"
    # If a number ends in " 9", it's almost certainly a "g"
    text = re.sub(r'(\d+)\s+9\b', r'\1 g', text)
    
    # Energy (Kcal) - Priority on the higher value (usually the 100g column)
    energy_matches = re.findall(r'energy\b[^0-9]*(\d+\.?\d*)', text, re.IGNORECASE)
    if energy_matches:
        # Pick the highest value found (560 kcal > 200 kcal)
        val = max([float(v) for v in energy_matches])
        if val < 1000:
            nutrition['energy'] = str(val) + ' kcal'
    
    # Protein
    protein_matches = re.findall(r'protein\b.*?(\d+\.?\d*)', text, re.IGNORECASE)
    if protein_matches:
        val = protein_matches[-1]
        nutrition['protein'] = val + 'g'
    
    # Total Fat
    fat_matches = re.findall(r'(?:total\s*)?fat\b.*?(\d+\.?\d*)', text, re.IGNORECASE)
    if fat_matches:
        val = fat_matches[-1]
        nutrition['total_fat'] = val + 'g'
    
    # Saturated Fat
    sat_matches = re.findall(r'saturated\b.*?fat\b.*?(\d+\.?\d*)', text, re.IGNORECASE)
    if sat_matches:
        val = sat_matches[-1]
        nutrition['saturated_fat'] = val + 'g'
    
    # Carbohydrates
    carb_matches = re.findall(r'carbohydrates?\b.*?(\d+\.?\d*)', text, re.IGNORECASE)
    if carb_matches:
        val = carb_matches[-1]
        nutrition['carbohydrates'] = val + 'g'
    
    # Sugars
    sugar_matches = re.findall(r'sugars?\b.*?(\d+\.?\d*)', text, re.IGNORECASE)
    if sugar_matches:
        val = sugar_matches[-1]
        nutrition['sugars'] = val + 'g'
    
    # Fiber
    fiber_matches = re.findall(r'fib(?:er|re)\b.*?(\d+\.?\d*)', text, re.IGNORECASE)
    if fiber_matches:
        val = fiber_matches[-1]
        nutrition['fiber'] = val + 'g'

    # Sodium (mg)
    sodium_matches = re.findall(r'sodium\b.*?(\d+\.?\d*)', text, re.IGNORECASE)
    if sodium_matches:
        # Pick the highest
        val = max([float(v) for v in sodium_matches])
        nutrition['sodium'] = str(val) + ' mg'
    
    # Serving Size
    serving_match = re.search(r'serv(?:ing|e)\s*size\s*[:]?\s*(\d+\.?\d*)\s*g', text, re.IGNORECASE)
    if not serving_match:
        serving_match = re.search(r'\(?(\d+\.?\d*)\s*g\)?\s*per\s*serve', text, re.IGNORECASE)
    if not serving_match:
        serving_match = re.search(r'per\s*serve.*?\(?(\d+\.?\d*)\s*g\)?', text, re.IGNORECASE)
    if serving_match:
        nutrition['serving_size'] = serving_match.group(1) + 'g'
    # Food Additives Extraction (e.g., E322, E-500, e211). Removes duplicates via set.
    additives = list(set([match.upper() for match in re.findall(r'\bE\s*[-]?\s*\d{3,4}[A-Za-z]?\b', text, re.IGNORECASE)]))

    return {
        'cleaned': text,
        'nutrition_values': nutrition,
        'additives': additives
    }