import openai
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = settings.openai_model
        self._initialize_client()
    
    def _initialize_client(self):
        if not self.api_key:
            logger.warning("OpenAI API key not provided. OpenAI features will be disabled.")
            return
        
        try:
            openai.api_key = self.api_key
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def analyze_medical_text(self, text: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        if not self.is_available():
            return {"error": "OpenAI client not configured"}
        
        try:
            system_prompt = self._get_system_prompt(analysis_type)
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this medical chart text:\n\n{text}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            analysis_result = response.choices[0].message.content
            return self._parse_analysis_result(analysis_result, analysis_type)
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _get_system_prompt(self, analysis_type: str) -> str:
        prompts = {
            "comprehensive": """You are a medical data extraction specialist. Analyze the provided nurse chart text and extract structured information. Return ONLY valid JSON with the following structure:
{
    "patient_demographics": {
        "name": "extracted name or null",
        "date": "extracted date or null",
        "patient_id": "extracted ID or null"
    },
    "vital_signs": {
        "blood_pressure": "systolic/diastolic or null",
        "pulse": "value in bpm or null",
        "temperature": "value in Celsius or null",
        "respiratory_rate": "value in breaths/min or null",
        "oxygen_saturation": "value in percentage or null"
    },
    "clinical_observations": {
        "notes": "summary of clinical notes",
        "assessments": ["list of assessment findings"],
        "interventions": ["list of nursing interventions"]
    },
    "confidence_level": "high/medium/low based on data completeness"
}""",
            "vitals_only": """Extract only vital signs from the medical chart text. Return JSON:
{
    "vital_signs": {
        "blood_pressure": "systolic/diastolic",
        "pulse": "bpm",
        "temperature": "Celsius",
        "respiratory_rate": "breaths/min",
        "oxygen_saturation": "%"
    }
}""",
            "summary": """Provide a concise clinical summary of the patient's condition based on the nurse chart. Return JSON:
{
    "clinical_summary": "brief summary",
    "key_findings": ["list of important findings"],
    "recommended_actions": ["list of suggested actions"]
}"""
        }
        return prompts.get(analysis_type, prompts["comprehensive"])
    
    def _parse_analysis_result(self, result: str, analysis_type: str) -> Dict[str, Any]:
        try:
            import json
            # Clean the response and parse JSON
            cleaned_result = result.strip()
            if cleaned_result.startswith("```json"):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.endswith("```"):
                cleaned_result = cleaned_result[:-3]
            
            return json.loads(cleaned_result)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            return {"raw_analysis": result, "parse_error": str(e)}
