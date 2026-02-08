from pathlib import Path
from typing import Generator, Dict, Any
from core.extraction.detector import FileTypeDetector, FileType
from core.extraction.pdf_stream import PDFExtractor
import logging

logger = logging.getLogger("meaning_engine")

class UniversalLoader:
    def __init__(self):
        # Lazy imports to avoid heavy dependencies if not needed
        from core.extraction.pdf_stream import PDFExtractor
        from core.extraction.image import ImageExtractor
        from core.extraction.media import MediaExtractor

        self._extractors = {
            FileType.PDF: PDFExtractor(),
            FileType.IMAGE: ImageExtractor(),
            FileType.AUDIO: MediaExtractor(),
            FileType.VIDEO: MediaExtractor(),
            # FileType.TEXT: TextExtractor() # To implement
        }

    def load(self, file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """
        Main entry point. Detects type and streams content.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type = FileTypeDetector.detect(file_path)
        logger.info(f"Loading {file_path.name} as {file_type.value}")

        extractor = self._extractors.get(file_type)
        
        if not extractor:
            logger.warning(f"No extractor for {file_type}. Skipping.")
            return

        yield from extractor.stream(file_path)
