# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# (Optional) basic build tools for scientific libs
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Environment and port
ENV FLASK_ENV=production
EXPOSE 5000

# Start your Flask + Rasa app
CMD ["python", "app.py"]
