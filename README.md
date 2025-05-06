# OpenGL Demo

A 3D demo application built with Python, OpenGL, and PyGame.

## Features

- 3D cube rendering with textures and shadows
- Movement controls in 3D space
- Camera controls with rotation on all axes
- Screenshot functionality with SQLite database storage
- Blue-themed menu interface

## Requirements

- Python 3.x
- PyGame
- PyOpenGL
- NumPy
- Pyrr
- SQLite3

## Installation

```
pip install pygame PyOpenGL PyOpenGL_accelerate numpy pyrr
```

## Running the Application

```
python openGL1/openGL1.py
```

## Controls

- **Movement**: WASD (X-Z plane), UP/DOWN (Y axis)
- **Rotation**: T/G (X axis), H/F (Y axis), Y/R (Z axis)
- **Screenshot**: M key
- **Shadow Map**: SPACE to toggle
- **Menu**: ESC to return

## Screenshots

Screenshots are saved to the `openGL1/screenshots` directory. Metadata is stored in a SQLite database.

## Docker (Linux Only)

The application can also be run in Docker on a Linux system.

### Build and Run with Docker Compose

```bash
# Allow X11 connections (required for display)
xhost +local:docker

# Build and run
docker-compose up
```

### Or with Direct Docker Commands

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