import sys
try:
    import pytesseract
    print("pytesseract installed")
except ImportError:
    print("pytesseract not installed")

try:
    import easyocr
    print("easyocr installed")
except ImportError:
    print("easyocr not installed")

try:
    import cv2
    print("opencv installed")
except ImportError:
    print("opencv not installed")

try:
    from PIL import Image
    print("pillow installed")
except ImportError:
    print("pillow not installed")
