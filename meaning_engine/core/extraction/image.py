import pytesseract
from PIL import Image
from pathlib import Path
from typing import Generator, Dict, Any
import logging
from core.extraction.base import BaseExtractor

logger = logging.getLogger("meaning_engine")

class ImageExtractor(BaseExtractor):
    def stream(self, file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """
        Extract text from images using OCR.
        """
        try:
            logger.info(f"Processing Image: {file_path.name}")
            img = Image.open(file_path)
            
            # Extract text
            text = pytesseract.image_to_string(img)
            
            # Simple heuristic for confidence (Tesseract has detailed data, simplified here)
            # Future: Use image_to_data for word-level confidence
            
            yield {
                "content": text,
                "page": 1, # Images are single 'page'
                "metadata": {
                    "source": file_path.name,
                    "extraction_mode": "OCR",
                    "type": "image"
                }
            }

        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            raise
