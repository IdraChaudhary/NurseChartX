import gradio as gr
import logging
import sys
import os
from typing import Dict, Any, Tuple

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ocr.easyocr_engine import EasyOCREngine
from src.ocr.tesseract_engine import TesseractEngine
from src.processing.text_parser import MedicalTextParser
from src.processing.data_validator import MedicalDataValidator
from src.llm.openai_client import OpenAIClient
from src.llm.cohere_client import CohereClient
from src.llm.anthropic_client import AnthropicClient
from config.settings import settings

logger = logging.getLogger(__name__)


class NurseChartXInterface:
    def __init__(self):
        self.ocr_engines = {
            "easyocr": EasyOCREngine(),
            "tesseract": TesseractEngine()
        }
        self.parser = MedicalTextParser()
        self.validator = MedicalDataValidator()
        
        # Initialize LLM clients
        self.llm_clients = {
            "openai": OpenAIClient(),
            "cohere": CohereClient(), 
            "anthropic": AnthropicClient()
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def process_medical_chart(
        self, 
        image, 
        ocr_engine: str,
        use_openai: bool,
        use_cohere: bool, 
        use_anthropic: bool,
        openai_key: str,
        cohere_key: str,
        anthropic_key: str,
        analysis_type: str
    ) -> Tuple[Dict[str, Any], str, str, str, str]:
        """
        Main processing pipeline for medical chart analysis
        """
        try:
            # Update API keys if provided
            if openai_key:
                self.llm_clients["openai"] = OpenAIClient(openai_key)
            if cohere_key:
                self.llm_clients["cohere"] = CohereClient(cohere_key)
            if anthropic_key:
                self.llm_clients["anthropic"] = AnthropicClient(anthropic_key)
            
            # Step 1: OCR Text Extraction
            extracted_text = self._extract_text_from_image(image, ocr_engine)
            if not extracted_text:
                return {}, "OCR failed - no text extracted", "", "", ""
            
            # Step 2: Medical Field Parsing
            structured_data = self.parser.parse_medical_fields(extracted_text)
            
            # Step 3: Data Validation
            validation_results = self.validator.validate_medical_data(structured_data)
            
            # Step 4: LLM Analysis
            llm_results = self._perform_llm_analysis(
                extracted_text, 
                structured_data,
                use_openai,
                use_cohere,
                use_anthropic,
                analysis_type
            )
            
            # Format outputs
            formatted_data = self._format_output_data(structured_data, validation_results)
            extraction_summary = self._generate_extraction_summary(structured_data, validation_results)
            
            return (
                formatted_data,
                extracted_text,
                llm_results.get("openai", "OpenAI analysis not requested"),
                llm_results.get("cohere", "Cohere analysis not requested"),
                llm_results.get("anthropic", "Anthropic analysis not requested")
            )
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {}, f"Processing error: {str(e)}", "", "", ""
    
    def _extract_text_from_image(self, image, engine: str) -> str:
        """Extract text using specified OCR engine"""
        try:
            if engine not in self.ocr_engines:
                engine = "easyocr"  # Default fallback
            
            ocr_engine = self.ocr_engines[engine]
            extracted_text = ocr_engine.extract_text(image)
            
            logger.info(f"OCR extraction completed using {engine}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def _perform_llm_analysis(
        self, 
        extracted_text: str,
        structured_data: Dict[str, Any],
        use_openai: bool,
        use_cohere: bool,
        use_anthropic: bool,
        analysis_type: str
    ) -> Dict[str, str]:
        """Perform analysis using configured LLM providers"""
        results = {}
        
        # Prepare context for LLM analysis
        analysis_context = f"""
        Extracted Text: {extracted_text}
        
        Structured Data: {structured_data}
        
        Analysis Request: {analysis_type}
        """
        
        if use_openai and self.llm_clients["openai"].is_available():
            try:
                openai_result = self.llm_clients["openai"].analyze_medical_text(
                    analysis_context, analysis_type
                )
                results["openai"] = self._format_llm_result(openai_result, "OpenAI")
            except Exception as e:
                results["openai"] = f"OpenAI analysis error: {str(e)}"
        
        if use_cohere and self.llm_clients["cohere"].is_available():
            try:
                cohere_result = self.llm_clients["cohere"].analyze_medical_text(analysis_context)
                results["cohere"] = self._format_llm_result(cohere_result, "Cohere")
            except Exception as e:
                results["cohere"] = f"Cohere analysis error: {str(e)}"
        
        if use_anthropic and self.llm_clients["anthropic"].is_available():
            try:
                anthropic_result = self.llm_clients["anthropic"].analyze_medical_text(analysis_context)
                results["anthropic"] = self._format_llm_result(anthropic_result, "Anthropic")
            except Exception as e:
                results["anthropic"] = f"Anthropic analysis error: {str(e)}"
        
        return results
    
    def _format_llm_result(self, result: Any, provider: str) -> str:
        """Format LLM result for display"""
        if isinstance(result, dict):
            if "error" in result:
                return f"{provider} Error: {result['error']}"
            else:
                # Pretty print dictionary results
                import json
                return f"{provider} Analysis:\n{json.dumps(result, indent=2)}"
        elif isinstance(result, str):
            return f"{provider} Analysis:\n{result}"
        else:
            return f"{provider} returned unexpected result type"
    
    def _format_output_data(self, data: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
        """Format structured data for display"""
        formatted = {
            "patient_information": {},
            "vital_signs": {},
            "clinical_data": {},
            "validation_results": validation
        }
        
        # Categorize data
        for key, value in data.items():
            if any(field in key for field in ["name", "id", "date", "time"]):
                formatted["patient_information"][key] = value
            elif any(field in key for field in ["blood_pressure", "pulse", "temperature", "respiratory", "oxygen"]):
                formatted["vital_signs"][key] = value
            elif any(field in key for field in ["notes", "assessment", "intervention", "pain", "consciousness"]):
                formatted["clinical_data"][key] = value
        
        return formatted
    
    def _generate_extraction_summary(self, data: Dict[str, Any], validation: Dict[str, Any]) -> str:
        """Generate a summary of the extraction results"""
        total_fields = len(data)
        valid_fields = len([v for v in data.values() if v])
        confidence = data.get("parsing_metadata", {}).get("confidence_score", 0)
        
        summary = f"""
        Extraction Summary:
        - Total fields processed: {total_fields}
        - Fields with data: {valid_fields}
        - Extraction confidence: {confidence * 100}%
        - Data validation: {'PASS' if validation.get('is_valid', False) else 'FAIL'}
        """
        
        if validation.get('errors'):
            summary += f"\nValidation Errors: {len(validation['errors'])}"
        if validation.get('warnings'):
            summary += f"\nValidation Warnings: {len(validation['warnings'])}"
        
        return summary.strip()
    
    def create_interface(self):
        """Create and configure the Gradio interface"""
        with gr.Blocks(
            title="NurseChartX - Medical Chart Analysis",
            theme=gr.themes.Soft(),
            css=".gradio-container {max-width: 1200px !important}"
        ) as interface:
            
            gr.Markdown("""
            # NurseChartX - AI-Powered Medical Chart Analysis
            Transform handwritten nurse charts into structured clinical data using advanced OCR and AI analysis.
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    # Input Section
                    image_input = gr.Image(
                        label="Upload Medical Chart",
                        type="pil",
                        sources=["upload", "clipboard"],
                        height=300
                    )
                    
                    with gr.Accordion("Processing Options", open=False):
                        ocr_engine = gr.Radio(
                            choices=["easyocr", "tesseract"],
                            value="easyocr",
                            label="OCR Engine"
                        )
                        
                        analysis_type = gr.Radio(
                            choices=["comprehensive", "vitals_only", "summary", "risk_assessment"],
                            value="comprehensive",
                            label="Analysis Type"
                        )
                    
                    with gr.Accordion("AI Provider Configuration", open=False):
                        use_openai = gr.Checkbox(label="Use OpenAI GPT", value=False)
                        use_cohere = gr.Checkbox(label="Use Cohere", value=False)
                        use_anthropic = gr.Checkbox(label="Use Anthropic Claude", value=False)
                        
                        openai_key = gr.Textbox(
                            label="OpenAI API Key",
                            type="password",
                            placeholder="sk-...",
                            visible=False
                        )
                        cohere_key = gr.Textbox(
                            label="Cohere API Key", 
                            type="password",
                            placeholder="...",
                            visible=False
                        )
                        anthropic_key = gr.Textbox(
                            label="Anthropic API Key",
                            type="password",
                            placeholder="sk-...",
                            visible=False
                        )
                    
                    process_btn = gr.Button("Analyze Medical Chart", variant="primary", size="lg")
                
                with gr.Column(scale=2):
                    # Output Section
                    with gr.Tab("Structured Data"):
                        data_output = gr.JSON(
                            label="Extracted Medical Data",
                            show_label=True
                        )
                    
                    with gr.Tab("Extracted Text"):
                        text_output = gr.Textbox(
                            label="OCR Extracted Text",
                            lines=10,
                            max_lines=20,
                            show_copy_button=True
                        )
                    
                    with gr.Tab("AI Analysis"):
                        with gr.Accordion("OpenAI Analysis", open=True):
                            openai_output = gr.Textbox(
                                label="GPT Analysis",
                                lines=6,
                                show_copy_button=True
                            )
                        
                        with gr.Accordion("Cohere Analysis", open=False):
                            cohere_output = gr.Textbox(
                                label="Cohere Analysis", 
                                lines=6,
                                show_copy_button=True
                            )
                        
                        with gr.Accordion("Anthropic Analysis", open=False):
                            anthropic_output = gr.Textbox(
                                label="Claude Analysis",
                                lines=6, 
                                show_copy_button=True
                            )
                    
                    with gr.Tab("Processing Summary"):
                        summary_output = gr.Textbox(
                            label="Extraction Summary",
                            lines=8,
                            show_copy_button=True
                        )
            
            # Event handlers for dynamic UI
            use_openai.change(
                lambda x: gr.update(visible=x),
                inputs=[use_openai],
                outputs=[openai_key]
            )
            
            use_cohere.change(
                lambda x: gr.update(visible=x),
                inputs=[use_cohere],
                outputs=[cohere_key]
            )
            
            use_anthropic.change(
                lambda x: gr.update(visible=x),
                inputs=[use_anthropic],
                outputs=[anthropic_key]
            )
            
            # Main processing event
            process_btn.click(
                fn=self.process_medical_chart,
                inputs=[
                    image_input,
                    ocr_engine,
                    use_openai,
                    use_cohere,
                    use_anthropic,
                    openai_key,
                    cohere_key,
                    anthropic_key,
                    analysis_type
                ],
                outputs=[
                    data_output,
                    text_output, 
                    openai_output,
                    cohere_output,
                    anthropic_output
                ]
            )
            
            # Examples section
            gr.Markdown("""
            ### Example Usage
            1. Upload a scanned or photographed nurse chart image
            2. Select processing options (OCR engine, analysis type)
            3. Configure AI providers if desired (requires API keys)
            4. Click 'Analyze Medical Chart' to process
            5. Review extracted data and AI analysis in respective tabs
            """)
        
        return interface


def main():
    """Launch the NurseChartX interface"""
    app = NurseChartXInterface()
    interface = app.create_interface()
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        debug=settings.debug
    )


if __name__ == "__main__":
    main()
