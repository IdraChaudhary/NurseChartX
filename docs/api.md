# NurseChartX API Documentation

## Overview

NurseChartX provides both a web interface and programmatic APIs for medical chart processing. This document covers the programmatic API usage.

## Core Components

### OCR Engine API

```python
from src.ocr.easyocr_engine import EasyOCREngine
from src.ocr.tesseract_engine import TesseractEngine

# Initialize OCR engine
ocr_engine = EasyOCREngine(languages=['en'])

# Extract text from image
extracted_text = ocr_engine.extract_text(image)

# Extract with confidence scores
detailed_results = ocr_engine.extract_text_with_confidence(image)
