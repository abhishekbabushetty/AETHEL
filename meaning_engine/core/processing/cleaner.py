import re
import unicodedata
import logging
from typing import Dict, Any

logger = logging.getLogger("meaning_engine")

class TextCleaner:
    """
    Standardizes text for optimal LLM consumption.
    """
    
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        # 1. Unicode Normalization (Fix mojibake, accents)
        text = unicodedata.normalize("NFKC", text)

        # 2. Fix Broken Hyphenation (line-break split words)
        # e.g., "re-\nport" -> "report", but keeps "x-ray"
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

        # 3. Collapse Whitespace
        # Replace non-breaking spaces
        text = text.replace('\xa0', ' ')
        # Collapse multiple spaces to one
        text = re.sub(r'[ \t]+', ' ', text)
        # Collapse excessive newlines (max 2)
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # 4. Remove Control Characters (except newlines/tabs)
        text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ["\n", "\t"])

        return text.strip()

    @staticmethod
    def is_boilerplate(text: str) -> bool:
        """
        Heuristic check for headers/footers/page numbers.
        """
        text = text.strip()
        
        # Empty
        if not text:
            return True
            
        # Page numbers "Page 1 of 10", "1", "- 1 -"
        if re.match(r'^Page \d+( of \d+)?$', text, re.IGNORECASE):
            return True
        if re.match(r'^-? ?\d+ ? -?$', text):
            return True

        # Too short to be meaningful content (context dependent)
        if len(text) < 5 and not re.search(r'[a-zA-Z]', text):
            return True

        return False

    def process_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleans a data chunk and updates metadata.
        """
        raw_text = chunk.get("content", "")
        cleaned_text = self.clean(raw_text)
        
        # Update content
        chunk["content_original"] = raw_text # Preserve original per "Detail-Preservation Rule"
        chunk["content"] = cleaned_text
        
        # Metadata update
        chunk.setdefault("metadata", {})
        chunk["metadata"]["cleaned"] = True
        chunk["metadata"]["char_reduction"] = len(raw_text) - len(cleaned_text)
        
        return chunk
