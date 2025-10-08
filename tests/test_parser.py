import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from processing.text_parser import MedicalTextParser
from processing.data_validator import MedicalDataValidator


class TestMedicalTextParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = MedicalTextParser()
        self.validator = MedicalDataValidator()
    
    def test_patient_name_extraction(self):
        """Test patient name extraction from various formats"""
        test_cases = [
            ("Name: John Smith", "John Smith"),
            ("Patient: Jane Doe", "Jane Doe"),
            ("Pt. Robert Johnson", "Robert Johnson"),
        ]
        
        for input_text, expected_name in test_cases:
            result = self.parser.parse_medical_fields(input_text)
            self.assertEqual(result.get("patient_name"), expected_name)
    
    def test_blood_pressure_extraction(self):
        """Test blood pressure extraction and validation"""
        test_text = "BP: 120/80\nBlood Pressure: 140/90"
        result = self.parser.parse_medical_fields(test_text)
        
        self.assertIn("blood_pressure", result)
        
        # Test validation
        validation = self.validator.validate_medical_data(result)
        self.assertTrue(validation["is_valid"])
    
    def test_vital_signs_extraction(self):
        """Test comprehensive vital signs extraction"""
        test_text = """
        Patient: Test Patient
        BP: 120/80
        Pulse: 72
        Temp: 37.2
        RR: 16
        SpO2: 98%
        """
        
        result = self.parser.parse_medical_fields(test_text)
        
        expected_fields = [
            "patient_name", "blood_pressure", "pulse", 
            "temperature", "respiratory_rate", "oxygen_saturation"
        ]
        
        for field in expected_fields:
            self.assertIn(field, result)
            self.assertIsNotNone(result[field])
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        # High confidence case (all essential fields present)
        complete_text = """
        Name: Complete Patient
        Date: 01/01/2024
        BP: 120/80
        Pulse: 72
        Temp: 37.0
        """
        
        complete_result = self.parser.parse_medical_fields(complete_text)
        complete_confidence = complete_result["parsing_metadata"]["confidence_score"]
        self.assertGreaterEqual(complete_confidence, 0.8)
        
        # Low confidence case (few fields present)
        incomplete_text = "Some random text without medical fields"
        incomplete_result = self.parser.parse_medical_fields(incomplete_text)
        incomplete_confidence = incomplete_result["parsing_metadata"]["confidence_score"]
        self.assertLessEqual(incomplete_confidence, 0.3)


class TestDataValidator(unittest.TestCase):
    
    def setUp(self):
        self.validator = MedicalDataValidator()
    
    def test_blood_pressure_validation(self):
        """Test blood pressure validation logic"""
        # Valid BP
        valid_result = self.validator._validate_blood_pressure("120/80")
        self.assertTrue(valid_result[0])
        
        # Invalid BP (systolic too low)
        invalid_result = self.validator._validate_blood_pressure("40/80")
        self.assertFalse(invalid_result[0])
        
        # Invalid format
        format_result = self.validator._validate_blood_pressure("120-80")
        self.assertFalse(format_result[0])
    
    def test_temperature_validation(self):
        """Test temperature validation"""
        # Valid temperature
        valid_result = self.validator._validate_temperature("37.5")
        self.assertTrue(valid_result[0])
        
        # Invalid temperature (too high)
        invalid_result = self.validator._validate_temperature("45.0")
        self.assertFalse(invalid_result[0])
        
        # Invalid format
        format_result = self.validator._validate_temperature("abc")
        self.assertFalse(format_result[0])


if __name__ == '__main__':
    unittest.main()
