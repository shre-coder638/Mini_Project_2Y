"""
OCR Service using EasyOCR for text extraction from images.
"""
import numpy as np
from PIL import Image
import os
import cv2
import easyocr


reader = easyocr.Reader(['en'])


class OCRService:

    @staticmethod
    def extract_text(image_path):

        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return ''

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Increase contrast
            gray = cv2.equalizeHist(gray)

            # Apply threshold (important for posters)
            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )

            results = reader.readtext(thresh)

            text = " ".join([r[1] for r in results])

            return text
        except Exception:
            # Fallback: try simple read
            try:
                results = reader.readtext(image_path)
                return " ".join([r[1] for r in results])
            except Exception:
                return ''


class TesseractOCRService:
    """
    Alternative OCR service using Tesseract.
    """
    
    def __init__(self, language='eng'):
        self.language = language
    
    def extract_text(self, image_path, detail_level='normal'):
        try:
            import pytesseract
            
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=self.language)
            all_text = [line.strip() for line in text.split('\n') if line.strip()]
            
            return {
                'success': True,
                'text': text.strip(),
                'all_text': all_text,
                'detailed_results': [],
                'language': self.language,
                'text_count': len(all_text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': None,
                'all_text': []
            }
    
    def extract_text_from_image(self, image, detail_level='normal'):
        try:
            import pytesseract
            
            text = pytesseract.image_to_string(image, lang=self.language)
            all_text = [line.strip() for line in text.split('\n') if line.strip()]
            
            return {
                'success': True,
                'text': text.strip(),
                'all_text': all_text,
                'detailed_results': [],
                'language': self.language,
                'text_count': len(all_text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': None,
                'all_text': []
            }


def get_ocr_service(provider="easyocr", languages=['en'], use_gpu=False):
    """
    Factory function to get the appropriate OCR service.
    """
    if provider.lower() == "tesseract":
        lang_code = '+'.join(languages) if isinstance(languages, list) else languages
        return TesseractOCRService(language=lang_code)
    else:
        return OCRService()
