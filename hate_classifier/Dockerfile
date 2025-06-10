# 1. Use official lightweight Python image
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy dependency files
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your application code
COPY . .

# 7. Expose the port FastAPI will run on
EXPOSE 5000

# 8. Command to run the app
CMD ["uvicorn", "hate_classifier:app", "--host", "0.0.0.0", "--port", "5000"]
