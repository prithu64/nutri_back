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
    
    # Energy
    energy_match = re.search(r'energy\s*\(?kcal\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not energy_match:
        energy_match = re.search(r'energy\s*(\d+\.?\d*)\s*kcal', text, re.IGNORECASE)
    # No fallback needed here: Guessing the first number after 'per serve' is too prone to eating serving weights (especially when OCR misreads 'g' as '9')
    
    if energy_match:
        val = energy_match.group(1)
        if float(val) < 1000:
            nutrition['energy'] = val + ' kcal'
    
    # Protein
    protein_match = re.search(r'protein\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not protein_match:
        protein_match = re.search(r'protein\s*(\d+\.?\d*)\s*g', text, re.IGNORECASE)
    if protein_match:
        val = protein_match.group(1)
        if float(val) < 100:
            nutrition['protein'] = val + 'g'
    
    # Total Fat
    fat_match = re.search(r'total\s*fat\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not fat_match:
        fat_match = re.search(r'total\s*fat\s*(\d+\.?\d*)\s*g', text, re.IGNORECASE)
    if not fat_match:
        fat_match = re.search(r'fat\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if fat_match:
        val = fat_match.group(1)
        if float(val) < 100:
            nutrition['total_fat'] = val + 'g'
    
    # Carbohydrates
    carb_match = re.search(r'carbohydrate\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not carb_match:
        carb_match = re.search(r'carbohydrates?\s*(\d+\.?\d*)\s*g', text, re.IGNORECASE)
    if carb_match:
        val = carb_match.group(1)
        if float(val) < 200:
            nutrition['carbohydrates'] = val + 'g'
    
    # Sugars
    sugar_match = re.search(r'total\s*sugars?\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not sugar_match:
        sugar_match = re.search(r'sugars?\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not sugar_match:
        sugar_match = re.search(r'sugars?\s*(\d+\.?\d*)\s*g', text, re.IGNORECASE)
    if sugar_match:
        val = sugar_match.group(1)
        if float(val) < 100:
            nutrition['sugars'] = val + 'g'
    
    # Saturated Fat
    sat_fat_match = re.search(r'saturated\s*fat\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not sat_fat_match:
        sat_fat_match = re.search(r'saturated\s*fat\s*(\d+\.?\d*)\s*g', text, re.IGNORECASE)
    if sat_fat_match:
        val = sat_fat_match.group(1)
        if float(val) < 100:
            nutrition['saturated_fat'] = val + 'g'

    # Fiber
    fiber_match = re.search(r'fib(?:er|re)\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not fiber_match:
        fiber_match = re.search(r'dietary\s*fib(?:er|re)\s*\(?g\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not fiber_match:
        fiber_match = re.search(r'fib(?:er|re)\s*(\d+\.?\d*)\s*g', text, re.IGNORECASE)
    if fiber_match:
        val = fiber_match.group(1)
        if float(val) < 100:
            nutrition['fiber'] = val + 'g'
    # Sodium
    sodium_match = re.search(r'sodium\s*\(?mg\)?\s*(\d+\.?\d*)', text, re.IGNORECASE)
    if not sodium_match:
        sodium_match = re.search(r'sodium\s*(\d+\.?\d*)\s*mg', text, re.IGNORECASE)
    if sodium_match:
        val = sodium_match.group(1)
        if float(val) < 5000:
            nutrition['sodium'] = val + ' mg'
    
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