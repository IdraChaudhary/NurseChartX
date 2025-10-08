import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ocr.easyocr_engine import EasyOCREngine
from ocr.tesseract_engine import TesseractEngine
from PIL import Image
import numpy as np


class TestOCREngines(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a simple test image with text
        self.test_image = Image.new('RGB', (100, 100), color='white')
        self.sample_text = "Patient Name: John Doe\nBP: 120/80\nTemp: 37.2"
    
    @patch('ocr.easyocr_engine.easyocr.Reader')
    def test_easyocr_initialization(self, mock_reader):
        """Test EasyOCR engine initialization"""
        mock_reader_instance = Mock()
        mock_reader.return_value = mock_reader_instance
        
        engine = EasyOCREngine(['en'])
        
        mock_reader.assert_called_once_with(['en'])
        self.assertIsNotNone(engine.reader)
    
    @patch('ocr.easyocr_engine.easyocr.Reader')
    def test_easyocr_text_extraction(self, mock_reader):
        """Test EasyOCR text extraction"""
        mock_reader_instance = Mock()
        mock_reader.return_value = mock_reader_instance
        mock_reader_instance.readtext.return_value = [
            "Patient Name: John Doe",
            "BP: 120/80", 
            "Temp: 37.2"
        ]
        
        engine = EasyOCREngine()
        result = engine.extract_text(self.test_image)
        
        self.assertIsInstance(result, str)
        self.assertIn("Patient", result)
        mock_reader_instance.readtext.assert_called_once()
    
    def test_tesseract_engine_initialization(self):
        """Test Tesseract engine initialization"""
        engine = TesseractEngine()
        self.assertIsNotNone(engine.engine)
    
    @patch('ocr.tesseract_engine.pytesseract.image_to_string')
    def test_tesseract_text_extraction(self, mock_tesseract):
        """Test Tesseract text extraction"""
        mock_tesseract.return_value = self.sample_text
        
        engine = TesseractEngine()
        result = engine.extract_text(self.test_image)
        
        self.assertIsInstance(result, str)
        self.assertIn("Patient", result)
        mock_tesseract.assert_called_once()


if __name__ == '__main__':
    unittest.main()
