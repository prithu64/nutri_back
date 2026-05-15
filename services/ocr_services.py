# services/ocr_services.py - SIMPLIFIED

import cv2
from services.ocr.preprocess import preprocess_methods
from services.ocr.ocr_engine import detect_text
from services.ocr.postprocess import clean_tokens


def extract_text(image_bytes):
    """Simple OCR with Smart Fallback to save computing time."""
    
    best_result = None
    best_score = 0
    core_keys = ['energy', 'total_fat', 'sodium', 'protein']
    
    print("Running OCR with Smart Fallback...")
    # Get all preprocessed versions of the image
    methods = preprocess_methods(image_bytes)
    
    # We want to re-order the methods list to try the most reliable one FIRST.
    # Unsharp and Grayscale usually perform best, so we pluck them out and run them first.
    method_dict = {name: img for name, img in methods}
    
    run_order = ["unsharp", "grayscale", "contrast", "denoised", "sharpened", "adaptive", "binary"]
    
    for name in run_order:
        if name not in method_dict:
            continue
            
        img = method_dict[name]
        words = detect_text(img, slow=False)
        result = clean_tokens(words)
        
        # Check how many extracted items are in our core required list
        nutrition_keys = result.get('nutrition_values', {}).keys()
        found_cores = sum(1 for k in core_keys if k in nutrition_keys)
        total_found = len(nutrition_keys)
        
        print(f"   {name}: found {total_found} nutrients total (Core: {found_cores}/4)")
        
        # Save the best result found so far
        if total_found > best_score:
            best_score = total_found
            best_result = result
            
        # EARLY EXIT CONDITIONS - This skips the rest of the loop to save massive time!
        if found_cores == 4:
            print("   ✅ SMART EXIT: Found all core nutrients! Stopping early to save time.")
            break
        elif total_found >= 5:
            # Alternate exit: if it found an abundance of items (like sugars/carbs) missing 1 core
            print("   ✅ SMART EXIT: Found 5+ total nutrients! Stopping early to save time.")
            break
            
    if best_result is None:
        best_result = {'cleaned': '', 'nutrition_values': {}}
    
    best_result['type'] = 'simple'
    return best_result