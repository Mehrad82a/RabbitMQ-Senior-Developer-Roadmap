# Dockerfile
FROM python:3.11-slim


# --- Environment Variables ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- Working Directory ---
WORKDIR /app


# --- Copy and Install Dependencies ---
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# --- Application Code ---
COPY . .
