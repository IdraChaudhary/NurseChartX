import anthropic
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class AnthropicClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = settings.anthropic_model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        if not self.api_key:
            logger.warning("Anthropic API key not provided. Claude features will be disabled.")
            return
        
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info("Anthropic client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def analyze_medical_text(self, text: str) -> Dict[str, Any]:
        if not self.is_available():
            return {"error": "Anthropic client not configured"}
        
        try:
            system_prompt = """You are a clinical data extraction specialist. Analyze nurse chart documentation and extract structured medical information. Focus on accuracy and clinical relevance."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Extract and structure the medical information from this nurse chart:\n\n{text}"
                }]
            )
            
            return {
                "claude_analysis": response.content[0].text,
                "model": self.model,
                "analysis_type": "structured_medical_extraction"
            }
            
        except Exception as e:
            logger.error(f"Anthropic analysis error: {e}")
            return {"error": f"Claude analysis failed: {str(e)}"}
    
    def risk_assessment(self, text: str) -> Dict[str, Any]:
        if not self.is_available():
            return {"error": "Anthropic client not configured"}
        
        try:
            system_prompt = """You are a clinical risk assessment specialist. Analyze nurse chart documentation and identify potential clinical risks or concerning patterns."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.1,
                system=system_prompt,
                messages=[{
                    "role": "user", 
                    "content": f"Perform a clinical risk assessment based on this nurse chart:\n\n{text}\n\nIdentify potential risks and concerning findings."
                }]
            )
            
            return {
                "risk_assessment": response.content[0].text,
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"Anthropic risk assessment error: {e}")
            return {"error": f"Risk assessment failed: {str(e)}"}
