# services/ocr/ocr_engine.py

import easyocr
import cv2
from .config import OCR_LANGUAGES, CONFIDENCE_THRESHOLD

# Initialize EasyOCR
reader = easyocr.Reader(OCR_LANGUAGES, gpu=False)

_LABEL_ALLOWLIST = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    " .,:;/%()[]+-"
)

def ocr_single_image(img, slow: bool = False):
    """OCR a single image"""
    # Fast-first for food labels; slow mode only when needed.
    results = reader.readtext(
        img,
        detail=1,
        paragraph=False,
        decoder="beamsearch" if slow else "greedy",
        allowlist=_LABEL_ALLOWLIST,
        # Rotation increases runtime a lot; keep to the most common cases.
        rotation_info=[90, 270] if slow else None,
    )
    words = []
    for bbox, text, confidence in results:
        if confidence >= CONFIDENCE_THRESHOLD:
            words.append(text)
    return words

def ocr_multiple_images(images):
    """OCR multiple images and combine results"""
    all_words = []
    seen = set()
    for img in images:
        words = ocr_single_image(img)
        for w in words:
            if w.lower() not in seen:
                all_words.append(w)
                seen.add(w.lower())
    return all_words

def detect_text(image, slow: bool = False):
    """Main OCR function"""
    return ocr_single_image(image, slow=slow)

def detect_text_multiple(images):
    return ocr_multiple_images(images)