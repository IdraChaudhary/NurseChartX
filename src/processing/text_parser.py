import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MedicalTextParser:
    def __init__(self):
        self.field_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, str]:
        return {
            # Patient demographics
            "patient_name": r"(?:Name|Patient|Pt\.?)[\s:\-]*([A-Za-z\s,]+)(?=\n|$)",
            "patient_id": r"(?:ID|MRN|Medical Record)[\s:\-]*([A-Za-z0-9\-]+)",
            "date": r"(?:Date|Dated?)[\s:\-]*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{2,4})",
            "time": r"(?:Time)[\s:\-]*([0-9]{1,2}:[0-9]{2}\s*(?:AM|PM)?)",
            
            # Vital signs
            "blood_pressure": r"(?:BP|Blood Pressure)[\s:\-]*([0-9]{2,3}\s*/\s*[0-9]{2,3})",
            "pulse": r"(?:Pulse|HR|Heart Rate)[\s:\-]*([0-9]{2,3})\s*(?:bpm|BPM)?",
            "temperature": r"(?:Temp|Temperature)[\s:\-]*([0-9]{2,3}\.?[0-9]?)\s*°?[CF]?",
            "respiratory_rate": r"(?:RR|Respiratory Rate|Respiration)[\s:\-]*([0-9]{1,2})\s*(?:/min|bpm)?",
            "oxygen_saturation": r"(?:SpO2|O2 Sat|Oxygen)[\s:\-]*([0-9]{2,3})\s*%?",
            
            # Clinical observations
            "pain_level": r"(?:Pain|Pain Level)[\s:\-]*([0-9]|10)\s*(?:/10)?",
            "consciousness": r"(?:Consciousness|Alertness)[\s:\-]*(Alert|Verbal|Pain|Unresponsive|AVPU)",
            
            # Medical notes patterns
            "assessment_note": r"(?:Assessment|Findings)[\s:\-]*(.+?)(?=\n\w+:|$)",
            "intervention_note": r"(?:Intervention|Action|Nursing)[\s:\-]*(.+?)(?=\n\w+:|$)",
            "general_notes": r"(?:Notes|Comments|Remarks)[\s:\-]*(.+?)(?=\n\w+|$)"
        }
    
    def parse_medical_fields(self, text: str) -> Dict[str, Any]:
        """Extract structured medical data from unstructured text"""
        results = {}
        
        # Extract using predefined patterns
        for field, pattern in self.field_patterns.items():
            matches = self._extract_with_pattern(text, pattern, field)
            if matches:
                results[field] = matches[0] if len(matches) == 1 else matches
        
        # Enhanced parsing for complex fields
        results.update(self._parse_vital_signs(text))
        results.update(self._parse_clinical_notes(text))
        results.update(self._calculate_derived_metrics(results))
        
        # Add metadata
        results["parsing_metadata"] = {
            "extraction_timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "fields_extracted": len([v for v in results.values() if v]),
            "confidence_score": self._calculate_confidence_score(results)
        }
        
        return results
    
    def _extract_with_pattern(self, text: str, pattern: str, field_name: str) -> List[str]:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            if matches:
                logger.debug(f"Found {len(matches)} matches for {field_name}")
                return [match.strip() for match in matches if match.strip()]
            return []
        except Exception as e:
            logger.error(f"Pattern extraction error for {field_name}: {e}")
            return []
    
    def _parse_vital_signs(self, text: str) -> Dict[str, Any]:
        """Enhanced vital signs parsing with validation"""
        vitals = {}
        
        # Blood pressure validation
        bp_match = re.search(self.field_patterns["blood_pressure"], text, re.IGNORECASE)
        if bp_match:
            bp_value = bp_match.group(1)
            systolic, diastolic = map(int, re.split(r'\s*/\s*', bp_value))
            if 50 <= systolic <= 250 and 30 <= diastolic <= 150:
                vitals["blood_pressure"] = {
                    "systolic": systolic,
                    "diastolic": diastolic,
                    "interpretation": self._interpret_blood_pressure(systolic, diastolic)
                }
        
        # Temperature parsing with unit conversion
        temp_match = re.search(r"([0-9]{2,3}\.?[0-9]?)\s*°?([CF])?", text, re.IGNORECASE)
        if temp_match:
            temp_value = float(temp_match.group(1))
            unit = temp_match.group(2) or 'C'  # Default to Celsius
            
            if unit.upper() == 'F':
                # Convert Fahrenheit to Celsius
                temp_value = (temp_value - 32) * 5/9
            
            vitals["temperature_celsius"] = round(temp_value, 1)
            vitals["temperature_interpretation"] = self._interpret_temperature(temp_value)
        
        return vitals
    
    def _parse_clinical_notes(self, text: str) -> Dict[str, Any]:
        """Extract and categorize clinical notes"""
        notes_section = {}
        
        # Find notes section (commonly after "Notes:" or similar)
        notes_pattern = r"(?:Notes|Comments|Nursing Notes)[\s:\-]*\n?(.+?)(?=\n[A-Z]|$)"
        notes_match = re.search(notes_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if notes_match:
            notes_text = notes_match.group(1).strip()
            notes_section["raw_notes"] = notes_text
            notes_section["word_count"] = len(notes_text.split())
            
            # Simple sentiment/urgency analysis
            urgency_indicators = ["stat", "urgent", "immediate", "critical", "emergent"]
            if any(indicator in notes_text.lower() for indicator in urgency_indicators):
                notes_section["urgency_level"] = "high"
            else:
                notes_section["urgency_level"] = "normal"
        
        return notes_section
    
    def _interpret_blood_pressure(self, systolic: int, diastolic: int) -> str:
        if systolic < 90 or diastolic < 60:
            return "hypotensive"
        elif systolic >= 140 or diastolic >= 90:
            return "hypertensive"
        elif systolic >= 120 or diastolic >= 80:
            return "elevated"
        else:
            return "normal"
    
    def _interpret_temperature(self, temp_c: float) -> str:
        if temp_c < 36.0:
            return "hypothermic"
        elif temp_c > 38.0:
            return "febrile"
        elif temp_c > 37.5:
            return "elevated"
        else:
            return "normal"
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived clinical metrics"""
        metrics = {}
        
        # Mean Arterial Pressure calculation
        if "blood_pressure" in data and isinstance(data["blood_pressure"], dict):
            bp = data["blood_pressure"]
            if "systolic" in bp and "diastolic" in bp:
                map_value = (2 * bp["diastolic"] + bp["systolic"]) / 3
                metrics["mean_arterial_pressure"] = round(map_value, 1)
        
        return metrics
    
    def _calculate_confidence_score(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted data quality"""
        essential_fields = ["patient_name", "date", "blood_pressure", "pulse", "temperature"]
        extracted_essential = sum(1 for field in essential_fields if field in data and data[field])
        
        confidence = extracted_essential / len(essential_fields)
        return round(confidence, 2)
