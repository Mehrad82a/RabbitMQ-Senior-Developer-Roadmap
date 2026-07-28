# Dockerfile
#FROM python:3.11-slim
FROM docker.arvancloud.ir/library/python:3.11-slim


# --- Environment Variables ---
# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1


# --- Working Directory ---
WORKDIR /app


# --- Install system dependencies ---
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# --- Copy and Install Dependencies ---
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# --- Application Code ---
COPY . .
