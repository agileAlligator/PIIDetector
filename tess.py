import cv2
import numpy as np

def CropSpace(img):
    """Crop whitespace from an OpenCV image."""
    if img is None:
        print("[ERROR] Invalid image input for CropSpace.")
        return None

    ## (1) convert to grayscale and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, threshed = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    ## (2) Morphological operations to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
    morphed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel)

    ## (3) Find the largest contour
    cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    if not cnts:
        print("[WARNING] No significant content found in image.")
        return img  # Return original image if no text found

    cnt = max(cnts, key=cv2.contourArea)  # Get the largest contour

    ## (4) Crop to bounding box
    x, y, w, h = cv2.boundingRect(cnt)
    cropped = img[y:y+h, x:x+w]

    return cropped  # ✅ Return the cropped image

def is_mostly_whitespace(image_cv) -> bool:
    """Detects if an image has a large amount of empty space."""
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    white_pixels = np.sum(threshold == 255)
    total_pixels = threshold.size
    white_ratio = white_pixels / total_pixels

    return white_ratio > 0.7  # If >70% whitespace, crop before OCR

def wrapper(image_cv):
    flag=0
    if is_mostly_whitespace(image_cv):
        # print("yes image is whitespace")
        flag=1
        return CropSpace(image_cv), flag
    else:
        return image_cv, flag
# img=cv2.imread("001.png")
# img=wrapper(img)
# cv2.imwrite("002.png",img)