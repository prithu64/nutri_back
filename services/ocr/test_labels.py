# services/ocr/test_labels.py

import sys
import json
from pathlib import Path

# Get the current file's location
current_file = Path(__file__).resolve()  # services/ocr/test_labels.py
current_dir = current_file.parent        # services/ocr/
project_root = current_dir.parent.parent # nutrisnap-back/

# Add project root to path so Python can find services.ocr_services
sys.path.insert(0, str(project_root))

from services.ocr_services import extract_text

def test_all_labels():
    """Test OCR on all images in the labels folder"""
    
    # Labels folder is inside the same directory as this script
    labels_folder = current_dir / "labels"  # services/ocr/labels/
    
    print(f"[INFO] Looking for labels in: {labels_folder}")
    
    if not labels_folder.exists():
        print(f"[ERROR] Labels folder not found!")
        print(f"   Please create: {labels_folder}")
        labels_folder.mkdir(exist_ok=True)
        return
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png']
    image_files = []
    
    for ext in image_extensions:
        # Case insensitive globbing inherently handled by Windows, but we use set to be safe
        image_files.extend(list(labels_folder.glob(f"*{ext}")))
        
    # Remove duplicates if any
    image_files = list(set(image_files))
    
    if not image_files:
        print(f"[ERROR] No image files found in {labels_folder}")
        print(f"   Please add .jpg or .png images to this folder")
        return
    
    print("=" * 70)
    print("NUTRISNAP OCR TEST")
    print("=" * 70)
    print(f"Found {len(image_files)} images to test\n")
    
    results = []
    
    for i, image_path in enumerate(image_files, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {image_path.name}")
        print(f"{'='*70}")
        
        try:
            # Read image bytes
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Run OCR
            result = extract_text(image_bytes)
            
            # Display results
            cleaned = result.get('cleaned', '')
            nutrition = result.get('nutrition_values', {})
            
            print(f"\n[TEXT] CLEANED TEXT (first 200 chars):")
            print(f"   {cleaned[:200]}...")
            
            print(f"\n[DATA] NUTRITION VALUES:")
            if nutrition:
                for key, value in nutrition.items():
                    print(f"   {key}: {value}")
            else:
                print("   [WARNING] No nutrition values extracted")
            
            # Store result
            results.append({
                'filename': image_path.name,
                'cleaned_text': cleaned,
                'nutrition_values': nutrition,
                'success': len(nutrition) > 0
            })
            
        except Exception as e:
            print(f"\n[ERROR]: {e}")
            results.append({
                'filename': image_path.name,
                'error': str(e),
                'success': False
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"\n[SUCCESSFUL]: {len(successful)}/{len(results)}")
    for r in successful:
        nutrients_count = len(r.get('nutrition_values', {}))
        print(f"   * {r['filename']}: {nutrients_count} nutrients")
    
    if failed:
        print(f"\n[FAILED]: {len(failed)}/{len(results)}")
        for r in failed:
            print(f"   - {r['filename']}: {r.get('error', 'No nutrients extracted')}")
    
    # Save results to JSON
    output_file = labels_folder / "test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] Detailed results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    test_all_labels()