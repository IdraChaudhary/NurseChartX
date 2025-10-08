import pytesseract
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TesseractEngine:
    def __init__(self):
        self.engine = pytesseract
        
    def extract_text(self, image: Image.Image) -> str:
        try:
            # Convert PIL Image to OpenCV format
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Perform OCR with optimized settings for medical charts
            text = self.engine.image_to_string(
                image_cv,
                config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/:.- '
            )
            
            logger.info("Tesseract OCR completed successfully")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Tesseract OCR error: {e}")
            return ""

    def extract_structured_data(self, image: Image.Image) -> dict:
        try:
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Extract data with different PSM modes for better accuracy
            data = self.engine.image_to_data(
                image_cv, 
                output_type=self.engine.Output.DICT,
                config='--psm 6'
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Structured data extraction error: {e}")
            return {}
