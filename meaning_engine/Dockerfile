FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Universal Semantic Layer
# tesseract-ocr: Text from images
# ffmpeg: Audio/Video extraction
# poppler-utils: PDF rendering
# libmagic1: File type detection
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    ffmpeg \
    libsm6 \
    libxext6 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure data directories exist
RUN mkdir -p input results logs

EXPOSE 8501

CMD ["streamlit", "run", "meaning_engine/app.py", "--server.address=0.0.0.0"]
