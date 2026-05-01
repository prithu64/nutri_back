# services/ocr/preprocess.py

import cv2
import numpy as np
from .config import RESIZE_SCALE, MAX_IMAGE_DIM

def decode_image(image_bytes):
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        return None

    # Heuristic crop for food labels:
    # - Phone photos are usually portrait with a barcode-heavy bottom area.
    # - Crop out the bottom portion to speed OCR and reduce noise.
    h, w = img.shape[:2]
    if h > w and h >= 400:
        y0 = int(h * 0.02)
        y1 = int(h * 0.88)
        y0 = max(0, min(y0, h - 1))
        y1 = max(y0 + 1, min(y1, h))
        img = img[y0:y1, :]

    return img

def resize_image(img):
    if img is None:
        return None
    h, w = img.shape[:2]
    scaled_w, scaled_h = int(w * RESIZE_SCALE), int(h * RESIZE_SCALE)
    # Cap size to keep OCR runtime reasonable on large phone photos
    max_dim = max(scaled_w, scaled_h)
    if max_dim > MAX_IMAGE_DIM:
        ratio = MAX_IMAGE_DIM / max_dim
        scaled_w = max(1, int(scaled_w * ratio))
        scaled_h = max(1, int(scaled_h * ratio))
    return cv2.resize(img, (scaled_w, scaled_h))

def preprocess_methods(image_bytes):
    """Try multiple preprocessing methods and return all"""
    img = decode_image(image_bytes)
    img = resize_image(img)
    results = []
    
    # Method 1: Grayscale only
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    results.append(('grayscale', gray))

    # Method 1b: Grayscale + Denoise (good for phone grain)
    denoised = cv2.fastNlMeansDenoising(gray, None, 12, 7, 21)
    results.append(('denoised', denoised))
    
    # Method 2: Grayscale + Contrast (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast = clahe.apply(gray)
    results.append(('contrast', contrast))
    
    # Method 3: Grayscale + Contrast + Sharpen
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(contrast, -1, kernel)
    results.append(('sharpened', sharpened))

    # Method 3b: Unsharp mask (often helps small text)
    blur = cv2.GaussianBlur(contrast, (0, 0), sigmaX=1.2)
    unsharp = cv2.addWeighted(contrast, 1.7, blur, -0.7, 0)
    results.append(('unsharp', unsharp))
    
    # Method 4: Binary (OTSU)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results.append(('binary', binary))
    
    # Method 5: Adaptive Threshold
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    results.append(('adaptive', adaptive))
    
    return results

def detect_table_and_split(img):
    """Detect if image has a table and split into columns"""
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()
    
    # Detect vertical lines
    edges = cv2.Canny(gray, 50, 150)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
    
    contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) >= 2:
        x_positions = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w < 10:
                x_positions.append(x + w//2)
        
        if len(x_positions) >= 2:
            x_positions.sort()
            images = []
            prev = 0
            for x in x_positions:
                if x - prev > 100:
                    images.append(gray[:, prev:x])
                prev = x
            images.append(gray[:, prev:])
            return images
    
    return None

def preprocess_with_table(image_bytes):
    """Preprocess and split tables"""
    img = decode_image(image_bytes)
    img = resize_image(img)
    return detect_table_and_split(img)