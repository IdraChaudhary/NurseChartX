import easyocr
import numpy as np
from PIL import Image
import logging
from typing import List, Tuple, Dict, Any

logger = logging.getLogger(__name__)


class EasyOCREngine:
    def __init__(self, languages: List[str] = None):
        self.languages = languages or ['en']
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        try:
            self.reader = easyocr.Reader(self.languages)
            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR reader: {e}")
            raise
    
    def extract_text(self, image: Image.Image) -> str:
        try:
            if self.reader is None:
                self._initialize_reader()
            
            # Convert PIL Image to numpy array
            image_array = np.array(image)
            
            # Perform OCR
            results = self.reader.readtext(image_array, detail=0)
            
            # Combine all text lines
            extracted_text = "\n".join(results)
            
            logger.info(f"Extracted {len(results)} text lines from image")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error during OCR extraction: {e}")
            return ""
    
    def extract_text_with_confidence(self, image: Image.Image) -> List[Tuple[str, float]]:
        try:
            if self.reader is None:
                self._initialize_reader()
            
            image_array = np.array(image)
            results = self.reader.readtext(image_array, detail=1)
            
            # Return text with confidence scores
            return [(text, float(confidence)) for (bbox, text, confidence) in results]
            
        except Exception as e:
            logger.error(f"Error during detailed OCR extraction: {e}")
            return []
