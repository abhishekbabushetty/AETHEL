import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Project Roots ---
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    INPUT_DIR: Path = BASE_DIR / "input"
    RESULTS_DIR: Path = BASE_DIR / "results"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # --- Core Identity ---
    SYSTEM_NAME: str = "Meaning Engine"
    VERSION: str = "0.1.0-alpha"

    # --- Qdrant (Memory) ---
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "universal_knowledge"

    # --- Massive File Handling ---
    STREAMING_CHUNK_SIZE: int = 1024 * 1024  # 1MB read buffer
    MAX_WORKERS: int = 4

    # --- Embeddings ---
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # --- Chunking Hierarchy ---
    CHUNK_MICRO: int = 500
    CHUNK_MESO: int = 2000
    CHUNK_MACRO: int = 10000

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_CONFIG_PATH: Path = BASE_DIR / "meaning_engine" / "logging.yaml"

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure critical paths
for path in [settings.INPUT_DIR, settings.RESULTS_DIR, settings.LOGS_DIR]:
    path.mkdir(parents=True, exist_ok=True)
