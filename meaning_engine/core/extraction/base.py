from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, Union
from pathlib import Path

class BaseExtractor(ABC):
    """
    Abstract Base Class for all modality extractors.
    Enforces streaming output to handle large files.
    """

    @abstractmethod
    def stream(self, file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """
        Yields chunks of extracted data.
        
        Yield format:
        {
            "content": str,          # The raw extracted text/transcript
            "page": int | None,      # Page number (for docs)
            "timestamp": float | None, # Timestamp (for audio/video)
            "metadata": dict         # application-specific metadata (OCR confidence, etc.)
        }
        """
        pass
