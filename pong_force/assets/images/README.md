# Image Assets

This directory should contain the following image files:

## Required Images:
- `icon.ico` - Game icon for executable
- `background.png` - Background image (optional)
- `paddle.png` - Paddle sprite (optional)
- `ball.png` - Ball sprite (optional)

## Image Specifications:
- Icon: 32x32 or 64x64 pixels, ICO format
- Sprites: PNG with transparency
- Background: 1000x600 pixels, PNG format

## Fallback:
If image files are not available, the game will use pygame's drawing functions to create shapes and effects.

## Usage:
The game automatically loads these images when available, or uses procedural graphics if not found.
