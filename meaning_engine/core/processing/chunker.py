from typing import List, Dict, Any, Generator
import re
from core.config import settings

class HierarchicalChunker:
    """
    Splits cleaned text into 3 levels of hierarchy:
    1. Micro (Search): Small, overlapping chunks for embeddings.
    2. Meso (Reasoning): Paragraph/Section based chunks for context.
    3. Macro (Summary): Large blocks for high-level summaries.
    """

    def __init__(self):
        self.micro_size = settings.CHUNK_MICRO
        self.meso_size = settings.CHUNK_MESO
        self.overlap = 100 # tokens/chars approx
        
    def chunk(self, processed_chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a processed extraction chunk (usually a page) and breaks it down.
        Returns a list of chunk objects with hierarchy metadata.
        """
        text = processed_chunk.get("content", "")
        base_meta = processed_chunk.get("metadata", {})
        
        chunks = []
        
        # --- Level 2: Meso (Sections/Paragraphs) ---
        # Split by double newline (paragraphs) -> roughly semantic
        sections = self._split_text(text, self.meso_size, separators=["\n\n", "\n", ". "])
        
        for sec_idx, section_text in enumerate(sections):
            meso_id = f"{base_meta.get('source')}_P{processed_chunk.get('page')}_S{sec_idx}"
            
            # Meso Chunk
            chunks.append({
                "chunk_id": meso_id,
                "content": section_text,
                "level": "meso",
                "metadata": {**base_meta, "parent_id": None}
            })
            
            # --- Level 1: Micro (Embeddings) ---
            # Split the section into smaller bits
            micro_parts = self._split_text(section_text, self.micro_size, separators=[". ", ", ", " "])
            
            for mic_idx, micro_text in enumerate(micro_parts):
                micro_id = f"{meso_id}_M{mic_idx}"
                chunks.append({
                    "chunk_id": micro_id,
                    "content": micro_text,
                    "level": "micro",
                    "metadata": {**base_meta, "parent_id": meso_id}
                })
                
        return chunks

    def _split_text(self, text: str, max_size: int, separators: List[str]) -> List[str]:
        """
        Recursive splitting logic.
        """
        final_chunks = []
        if len(text) <= max_size:
            return [text]
            
        # Try separators in order
        for sep in separators:
            parts = text.split(sep)
            good_parts = []
            current_part = ""
            
            for part in parts:
                # Re-add separator if it's not a newline (rough heuristic)
                if sep not in ["\n\n", "\n"]:
                    part += sep
                    
                if len(current_part) + len(part) < max_size:
                    current_part += part
                else:
                    if current_part:
                        good_parts.append(current_part)
                    current_part = part
            
            if current_part:
                good_parts.append(current_part)
                
            # Check if this separator worked well (didn't leave huge chunks)
            if all(len(p) <= max_size * 1.5 for p in good_parts): # Allow slight overflow
                return good_parts
                
        # Fallback: Hard slice
        return [text[i:i+max_size] for i in range(0, len(text), max_size-self.overlap)]
