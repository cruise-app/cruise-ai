# 1. Use official slim Python base image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Install OS dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy dependencies and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy application source code
COPY . .

# 6. Create audio_input folder at build time
RUN mkdir -p audio_input

# 7. Expose the port your FastAPI app runs on
EXPOSE 8000

# 8. Command to run your app
CMD ["uvicorn", "recognizer:app", "--host", "0.0.0.0", "--port", "8000"]
