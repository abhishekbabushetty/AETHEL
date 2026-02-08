import magic
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger("meaning_engine")

class FileType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    TEXT = "text"
    UNKNOWN = "unknown"

class FileTypeDetector:
    @staticmethod
    def detect(file_path: Path) -> FileType:
        """
        Detects the file type using python-magic (libmagic).
        Reads the file header bytes for accuracy.
        """
        try:
            mime = magic.from_file(str(file_path), mime=True)
            logger.debug(f"Detected MIME type for {file_path.name}: {mime}")

            if mime == "application/pdf":
                return FileType.PDF
            elif mime.startswith("image/"):
                return FileType.IMAGE
            elif mime.startswith("audio/"):
                return FileType.AUDIO
            elif mime.startswith("video/"):
                return FileType.VIDEO
            elif mime.startswith("text/") or mime == "application/json":
                return FileType.TEXT
            else:
                logger.warning(f"Unsupported MIME type: {mime}")
                return FileType.UNKNOWN
        except Exception as e:
            logger.error(f"Error detecting file type: {e}")
            return FileType.UNKNOWN
