import cohere
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class CohereClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.cohere_api_key
        self.model = settings.cohere_model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        if not self.api_key:
            logger.warning("Cohere API key not provided. Cohere features will be disabled.")
            return
        
        try:
            self.client = cohere.Client(self.api_key)
            logger.info("Cohere client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {e}")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def analyze_medical_text(self, text: str) -> Dict[str, Any]:
        if not self.is_available():
            return {"error": "Cohere client not configured"}
        
        try:
            prompt = f"""Analyze this nurse chart text and extract medical information in a structured way:

{text}

Please provide:
1. Patient identification information
2. Vital signs and measurements
3. Clinical observations and notes
4. Nursing assessments and interventions

Format the response as a clear, structured summary."""

            response = self.client.chat(
                message=prompt,
                model=self.model,
                temperature=0.1
            )
            
            return {
                "cohere_analysis": response.text,
                "model": self.model,
                "analysis_type": "clinical_data_extraction"
            }
            
        except Exception as e:
            logger.error(f"Cohere analysis error: {e}")
            return {"error": f"Cohere analysis failed: {str(e)}"}
    
    def clinical_summary(self, text: str) -> str:
        if not self.is_available():
            return "Cohere client not available"
        
        try:
            prompt = f"""Provide a concise clinical summary of this nurse chart:

{text}

Focus on:
- Patient's current condition
- Key vital sign trends
- Important clinical findings
- Recommended monitoring"""

            response = self.client.chat(
                message=prompt,
                model=self.model,
                temperature=0.1
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Cohere summary error: {e}")
            return f"Summary generation failed: {str(e)}"
