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
- Updated GPU drivers (required for optimal performance)

## Important Notes

- **GPU Drivers**: Please ensure your GPU drivers are up to date for optimal performance and compatibility
- **Mac Users**: Performance may be suboptimal on Mac systems, especially on M1/M2 chips due to OpenGL limitations
- **Windows Users**: Make sure you have the latest graphics drivers installed from your GPU manufacturer's website
- **External Tools**: Do NOT use MSI Afterburner, RivaTuner, or any other system monitoring/overlay software while running this application as they can interfere with OpenGL rendering and cause crashes

## Installation

```bash
# Install required packages
pip install pygame PyOpenGL PyOpenGL_accelerate numpy pyrr
```

## Running the Application

```bash
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

---
Last updated: May 2023 