# Sound Assets

This directory should contain the following sound files:

## Required Sounds:
- `hit.wav` - Paddle collision sound
- `score.wav` - Scoring sound effect  
- `force.wav` - Force push activation sound
- `background.wav` - Background music (optional)

## Sound Specifications:
- Format: WAV, 44.1kHz, 16-bit
- Duration: 0.1-2 seconds for effects, longer for music
- File size: Under 1MB per sound effect

## Fallback:
If sound files are not available, the game will generate procedural sounds using pygame's audio capabilities.

## Usage:
The game automatically loads these sounds when available, or creates procedural alternatives if not found.
