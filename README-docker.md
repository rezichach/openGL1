# Docker Setup for OpenGL Demo (Linux Only)

This guide explains how to run the OpenGL Demo application using Docker on Linux.

## Prerequisites

- Docker installed on Linux
- Docker Compose installed (optional)
- X11 server running

## Quick Start

### 1. Prepare the Environment

First, allow Docker to connect to your X11 display:

```bash
xhost +local:docker
```

### 2. Option A: Using Docker Compose (Recommended)

```bash
# Build and run in one command
docker-compose up

# To run in the background
docker-compose up -d

# To stop the container
docker-compose down
```

### 2. Option B: Using Direct Docker Commands

```bash
# Build the image
docker build -t opengl1-app .

# Run the container
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ./openGL1/screenshots:/app/openGL1/screenshots \
    --network host \
    opengl1-app
```

## Important Notes

- **Screenshots**: All screenshots are saved to `openGL1/screenshots/` which is shared between the container and host.
- **Database**: The SQLite database is also shared between container and host.
- **Controls**: All keyboard controls work the same as in the non-Docker version.

## Troubleshooting

- If you see "Cannot open display" errors, ensure you ran `xhost +local:docker`
- If permissions issues occur with the screenshots directory, run:
  ```bash
  mkdir -p openGL1/screenshots && chmod 777 openGL1/screenshots
  ``` 