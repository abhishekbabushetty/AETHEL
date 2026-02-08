from pdf2image import convert_from_path
import pytesseract
from pypdf import PdfReader
from pathlib import Path
from typing import Generator, Dict, Any
import logging
from core.extraction.base import BaseExtractor

logger = logging.getLogger("meaning_engine")

class PDFExtractor(BaseExtractor):
    def stream(self, file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """
        Stream PDF pages.
        Adaptive Strategy:
        - If page has digital text -> Return text.
        - If page is empty/image -> Run OCR.
        """
        try:
            reader = PdfReader(str(file_path))
            total_pages = len(reader.pages)
            logger.info(f"Processing PDF: {file_path.name} ({total_pages} pages)")

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                
                # Heuristic: If text is very short, it's likely a scan or image-heavy page
                is_scanned = len(text.strip()) < 50
                
                if is_scanned:
                    logger.debug(f"Page {page_num+1} seems scanned. Running OCR...")
                    text = self._ocr_page(file_path, page_num + 1)
                    mode = "OCR"
                else:
                    mode = "DIGITAL"

                yield {
                    "content": text,
                    "page": page_num + 1,
                    "total_pages": total_pages,
                    "metadata": {
                        "source": file_path.name,
                        "extraction_mode": mode,
                        "is_ocr": is_scanned
                    }
                }

        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            raise

    def _ocr_page(self, file_path: Path, page_num: int) -> str:
        """
        Render specific page to image and transcribe.
        """
        try:
            # Convert single page to image (lazy)
            images = convert_from_path(
                str(file_path), 
                first_page=page_num, 
                last_page=page_num
            )
            if not images:
                return ""
            
            # Run Tesseract
            # We can capture confidence data here if we use image_to_data
            text = pytesseract.image_to_string(images[0])
            return text
        except Exception as e:
            logger.error(f"OCR Failed for page {page_num}: {e}")
            return ""
