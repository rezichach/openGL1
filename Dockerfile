FROM python:3.10-slim

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y \
        libgl1-mesa-glx \
        libgl1-mesa-dri \
        libglu1-mesa \
        libx11-6 \
        libxext6 \
        libsm6 \
        libxrender1 \
        x11-xserver-utils \
        sqlite3 \
        xvfb \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Create screenshots directory with proper permissions
RUN mkdir -p openGL1/screenshots && \
    chmod 777 openGL1/screenshots

# Install Python dependencies
RUN pip install --no-cache-dir pygame PyOpenGL PyOpenGL_accelerate numpy pyrr sqlite3

# Don't set a default DISPLAY - get it from the environment
# ENV DISPLAY=:0

# Use same volume path as in docker-compose.yml
VOLUME ["/app/openGL1/screenshots"]

CMD ["python", "openGL1/openGL1.py"] 