import re
from typing import Dict, Any, List, Tuple
from datetime import datetime


class MedicalDataValidator:
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, callable]:
        return {
            "patient_name": self._validate_name,
            "patient_id": self._validate_id,
            "date": self._validate_date,
            "blood_pressure": self._validate_blood_pressure,
            "pulse": self._validate_pulse,
            "temperature": self._validate_temperature,
            "respiratory_rate": self._validate_respiratory_rate,
            "oxygen_saturation": self._validate_oxygen_saturation
        }
    
    def validate_medical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "validated_fields": {}
        }
        
        for field, value in data.items():
            if field in self.validation_rules and value:
                is_valid, message = self.validation_rules[field](value)
                
                if not is_valid:
                    validation_results["is_valid"] = False
                    validation_results["errors"].append(f"{field}: {message}")
                elif message:
                    validation_results["warnings"].append(f"{field}: {message}")
                
                validation_results["validated_fields"][field] = {
                    "value": value,
                    "valid": is_valid,
                    "message": message
                }
        
        return validation_results
    
    def _validate_name(self, name: str) -> Tuple[bool, str]:
        if not re.match(r"^[A-Za-z\s,\-\.']{2,50}$", name.strip()):
            return False, "Invalid name format"
        return True, ""
    
    def _validate_id(self, patient_id: str) -> Tuple[bool, str]:
        if not re.match(r"^[A-Za-z0-9\-]{4,20}$", str(patient_id)):
            return False, "Invalid patient ID format"
        return True, ""
    
    def _validate_date(self, date_str: str) -> Tuple[bool, str]:
        try:
            # Try multiple date formats
            formats = ["%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%Y-%m-%d"]
            for fmt in formats:
                try:
                    datetime.strptime(date_str, fmt)
                    return True, ""
                except ValueError:
                    continue
            return False, "Invalid date format"
        except:
            return False, "Date parsing error"
    
    def _validate_blood_pressure(self, bp: Any) -> Tuple[bool, str]:
        if isinstance(bp, dict) and "systolic" in bp and "diastolic" in bp:
            systolic, diastolic = bp["systolic"], bp["diastolic"]
        else:
            # Parse string format "120/80"
            if isinstance(bp, str):
                parts = bp.split('/')
                if len(parts) != 2:
                    return False, "Invalid blood pressure format"
                try:
                    systolic, diastolic = int(parts[0]), int(parts[1])
                except ValueError:
                    return False, "Blood pressure values must be numeric"
            else:
                return False, "Invalid blood pressure data type"
        
        if not (50 <= systolic <= 250):
            return False, f"Systolic BP {systolic} outside valid range (50-250)"
        if not (30 <= diastolic <= 150):
            return False, f"Diastolic BP {diastolic} outside valid range (30-150)"
        if systolic <= diastolic:
            return False, "Systolic BP must be greater than diastolic BP"
        
        return True, ""
    
    def _validate_pulse(self, pulse: Any) -> Tuple[bool, str]:
        try:
            pulse_val = int(pulse)
            if not (30 <= pulse_val <= 200):
                return False, f"Pulse {pulse_val} outside valid range (30-200)"
            return True, ""
        except (ValueError, TypeError):
            return False, "Pulse must be a numeric value"
    
    def _validate_temperature(self, temp: Any) -> Tuple[bool, str]:
        try:
            temp_val = float(temp)
            if not (35.0 <= temp_val <= 42.0):  # Celsius range
                return False, f"Temperature {temp_val}°C outside valid range (35.0-42.0)"
            return True, ""
        except (ValueError, TypeError):
            return False, "Temperature must be a numeric value"
    
    def _validate_respiratory_rate(self, rr: Any) -> Tuple[bool, str]:
        try:
            rr_val = int(rr)
            if not (8 <= rr_val <= 40):
                return False, f"Respiratory rate {rr_val} outside valid range (8-40)"
            return True, ""
        except (ValueError, TypeError):
            return False, "Respiratory rate must be a numeric value"
    
    def _validate_oxygen_saturation(self, spo2: Any) -> Tuple[bool, str]:
        try:
            spo2_val = int(spo2)
            if not (70 <= spo2_val <= 100):
                return False, f"Oxygen saturation {spo2_val}% outside valid range (70-100)"
            return True, ""
        except (ValueError, TypeError):
            return False, "Oxygen saturation must be a numeric value"
