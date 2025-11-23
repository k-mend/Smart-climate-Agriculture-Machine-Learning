# Use Python 3.10 slim image (Lightweight but Debian-based for compatibility)
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /project

# --- INSTALL SYSTEM DEPENDENCIES ---
# OSMnx and Geopandas require C++ libraries (libspatialindex, gdal) 
# that are not included in standard Python images.
RUN apt-get update && apt-get install -y \
    g++ \
    make \
    libspatialindex-dev \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker's layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the specific folders needed for the application
# We copy them into /project/app, /project/data, etc.
COPY app/ ./app/
COPY data/ ./data/
COPY models/ ./models/

# Create a directory for cached road data (if your code saves it here)
RUN mkdir -p data/road_data

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the application
# Note: Since we are in /project, and main.py is in app/, we call app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
