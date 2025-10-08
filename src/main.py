#!/usr/bin/env python3
"""
NurseChartX - Main Application Entry Point
AI-powered medical chart extraction and analysis system.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.interface.gradio_app import NurseChartXInterface
from config.settings import settings


def setup_logging(verbose: bool = False):
    """Configure application logging"""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('nursechartx.log', mode='a', encoding='utf-8')
        ]
    )
    
    # Reduce verbosity for some noisy libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="NurseChartX - Medical Chart Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch web interface
  python main.py --web
  
  # Process single image file
  python main.py --image chart.jpg --output results.json
  
  # Batch process directory
  python main.py --batch ./charts/ --output ./results/
        """
    )
    
    parser.add_argument(
        '--web', 
        action='store_true',
        help='Launch web interface'
    )
    
    parser.add_argument(
        '--image',
        type=str,
        help='Process single medical chart image'
    )
    
    parser.add_argument(
        '--batch',
        type=str, 
        help='Process directory of medical chart images'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./output',
        help='Output directory for results (default: ./output)'
    )
    
    parser.add_argument(
        '--ocr-engine',
        choices=['easyocr', 'tesseract'],
        default='easyocr',
        help='OCR engine to use (default: easyocr)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=7860,
        help='Web interface port (default: 7860)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Web interface host (default: 0.0.0.0)'
    )
    
    return parser.parse_args()


def process_single_image(image_path: str, output_dir: str, ocr_engine: str):
    """Process a single medical chart image"""
    from src.ocr.easyocr_engine import EasyOCREngine
    from src.ocr.tesseract_engine import TesseractEngine
    from src.processing.text_parser import MedicalTextParser
    from src.processing.data_validator import MedicalDataValidator
    from PIL import Image
    import json
    
    logging.info(f"Processing image: {image_path}")
    
    try:
        # Load image
        image = Image.open(image_path)
        
        # Initialize processors
        if ocr_engine == 'easyocr':
            ocr_processor = EasyOCREngine()
        else:
            ocr_processor = TesseractEngine()
        
        parser = MedicalTextParser()
        validator = MedicalDataValidator()
        
        # Process image
        extracted_text = ocr_processor.extract_text(image)
        
        if not extracted_text:
            logging.error(f"No text extracted from {image_path}")
            return None
        
        # Parse and validate
        structured_data = parser.parse_medical_fields(extracted_text)
        validation_results = validator.validate_medical_data(structured_data)
        
        # Prepare results
        results = {
            "source_image": image_path,
            "extracted_text": extracted_text,
            "structured_data": structured_data,
            "validation_results": validation_results,
            "processing_metadata": {
                "ocr_engine": ocr_engine,
                "timestamp": import datetime; datetime.datetime.now().isoformat()
            }
        }
        
        # Save results
        output_path = Path(output_dir) / f"{Path(image_path).stem}_results.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Results saved to: {output_path}")
        return results
        
    except Exception as e:
        logging.error(f"Error processing {image_path}: {e}")
        return None


def process_batch_directory(input_dir: str, output_dir: str, ocr_engine: str):
    """Process all images in a directory"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        logging.error(f"Input directory does not exist: {input_dir}")
        return
    
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    image_files = [
        f for f in input_path.iterdir() 
        if f.suffix.lower() in supported_formats and f.is_file()
    ]
    
    if not image_files:
        logging.warning(f"No supported image files found in {input_dir}")
        return
    
    logging.info(f"Found {len(image_files)} images to process")
    
    results = []
    for image_file in image_files:
        result = process_single_image(str(image_file), output_dir, ocr_engine)
        if result:
            results.append(result)
    
    # Generate batch summary
    summary = {
        "batch_processing_summary": {
            "input_directory": input_dir,
            "output_directory": output_dir,
            "total_images": len(image_files),
            "successfully_processed": len(results),
            "success_rate": len(results) / len(image_files) * 100,
            "ocr_engine": ocr_engine
        }
    }
    
    summary_path = Path(output_dir) / "batch_processing_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(summary, f, indent=2)
    
    logging.info(f"Batch processing complete. Summary: {summary_path}")


def launch_web_interface(host: str, port: int):
    """Launch the Gradio web interface"""
    logging.info(f"Starting NurseChartX web interface on {host}:{port}")
    
    app = NurseChartXInterface()
    interface = app.create_interface()
    
    interface.launch(
        server_name=host,
        server_port=port,
        share=False,
        show_error=True,
        debug=settings.debug
    )


def main():
    """Main application entry point"""
    args = parse_arguments()
    setup_logging(args.verbose)
    
    logging.info("Starting NurseChartX Medical Chart Analysis System")
    logging.info(f"Application version: {settings.app_version}")
    logging.info(f"Debug mode: {settings.debug}")
    
    try:
        if args.web:
            launch_web_interface(args.host, args.port)
        
        elif args.image:
            process_single_image(args.image, args.output, args.ocr_engine)
        
        elif args.batch:
            process_batch_directory(args.batch, args.output, args.ocr_engine)
        
        else:
            # Default to web interface if no arguments provided
            logging.info("No specific mode specified, launching web interface")
            launch_web_interface(args.host, args.port)
    
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)
    
    logging.info("NurseChartX application finished")


if __name__ == "__main__":
    main()
