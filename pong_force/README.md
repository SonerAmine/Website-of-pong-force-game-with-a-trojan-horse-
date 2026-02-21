# 🎮 Pong Force

**Revolutionary Pong with Force Push Mechanics**

A modern take on the classic Pong game featuring the innovative Force Push mechanic that adds strategic depth and intense multiplayer action.

## ✨ Features

### 🎯 Core Gameplay
- **2-Player Multiplayer**: Local or LAN multiplayer support
- **Force Push Mechanic**: Strategic power move that dramatically increases ball speed
- **Dynamic Physics**: Realistic ball physics with speed increases and angle changes
- **Competitive Scoring**: First to 10 points wins

### ⚡ Force Push System
- **Charge Over Time**: Force meter fills automatically every 10 seconds
- **Strategic Timing**: Must be close to ball to activate successfully
- **Risk/Reward**: Failed attempts stun your paddle for 0.5 seconds
- **Visual Effects**: Glowing effects, particle bursts, and screen shake

### 🎨 Visual Design
- **Neon Arcade Theme**: Futuristic glowing aesthetics
- **Particle Effects**: Dynamic visual feedback for all actions
- **Smooth Animations**: 60 FPS gameplay with fluid motion
- **Screen Effects**: Shake effects and glowing trails

### 🌐 Networking
- **LAN Multiplayer**: Play with friends over local network
- **Client-Server Architecture**: Stable multiplayer with low latency
- **Automatic Reconnection**: Handles network interruptions gracefully

## 🚀 Quick Start

### Installation

1. **Clone or Download**
   ```bash
   git clone <repository-url>
   cd pong_force
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Game**
   ```bash
   python main.py
   ```

### Game Modes

#### Local Multiplayer
```bash
python main.py
# Select option 3: Local Multiplayer
```

#### Host Game (Server)
```bash
python main.py --server
# Or select option 1 from menu
```

#### Join Game (Client)
```bash
python main.py --client --host <server-ip>
# Or select option 2 from menu
```

## 🎮 Controls

### Player 1 (Left Paddle)
- **Move**: Arrow Keys (↑↓)
- **Force Push**: SPACE

### Player 2 (Right Paddle)
- **Move**: W/S Keys
- **Force Push**: SHIFT

### General Controls
- **Pause**: ESC
- **Restart**: R
- **Quit**: ESC (in menu) or Close Window

## 🎯 How to Play

### Basic Gameplay
1. **Move your paddle** to hit the ball
2. **Score points** by getting the ball past your opponent
3. **First to 10 points wins**

### Force Push Strategy
1. **Wait for your force meter to fill** (glows when ready)
2. **Get close to the ball** before activating
3. **Press Force Push key** to dramatically increase ball speed
4. **Time it perfectly** - failed attempts stun your paddle!

### Advanced Tips
- **Use paddle positioning** to control ball direction
- **Save force pushes** for critical moments
- **Watch your opponent's force meter** to anticipate their moves
- **Practice timing** - force push range is limited

## 🏗️ Technical Details

### System Requirements
- **Python**: 3.7 or higher
- **Pygame**: 2.1.0 or higher
- **RAM**: 100MB minimum
- **Network**: For multiplayer (LAN)

### Architecture
```
pong_force/
├── main.py              # Entry point
├── config.py            # Game configuration
├── game/                # Core game logic
│   ├── game_loop.py     # Main game loop
│   ├── paddle.py        # Paddle physics
│   ├── ball.py          # Ball physics
│   ├── power.py         # Force push system
│   ├── scoreboard.py    # UI and scoring
│   └── effects.py       # Visual effects
├── network/             # Multiplayer networking
│   ├── server.py        # Game server
│   └── client.py        # Game client
└── assets/              # Game assets
    ├── sounds/          # Audio files
    ├── images/          # Graphics
    └── fonts/           # Font files
```

### Networking Protocol
- **Protocol**: TCP for reliability
- **Port**: 5555 (configurable)
- **Update Rate**: 60 Hz
- **Message Types**: Input, game state, force push, pause/restart

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Game Settings
WIN_SCORE = 10           # Points to win
FORCE_COOLDOWN = 10      # Seconds between force pushes
BALL_SPEED = 6           # Base ball speed
PADDLE_SPEED = 8         # Paddle movement speed

# Visual Settings
WINDOW_WIDTH = 1000      # Screen width
WINDOW_HEIGHT = 600      # Screen height
FPS = 60                 # Target frame rate

# Network Settings
SERVER_PORT = 5555       # Server port
NETWORK_UPDATE_RATE = 60 # Network updates per second
```

## 📦 Building Executable

### Using PyInstaller

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Build Executable**
   ```bash
   pyinstaller --onefile --windowed --add-data "assets;assets" main.py
   ```

3. **Test Executable**
   ```bash
   # Host game
   dist/main.exe --server
   
   # Join game
   dist/main.exe --client --host <server-ip>
   ```

### Distribution
- **Windows**: `main.exe` (standalone)
- **macOS**: `main` (may need pygame dependencies)
- **Linux**: `main` (may need pygame dependencies)

## 🐛 Troubleshooting

### Common Issues

**Game won't start**
- Check Python version (3.7+ required)
- Install pygame: `pip install pygame`
- Check for missing dependencies

**Multiplayer connection failed**
- Check firewall settings
- Verify server IP and port
- Ensure both players are on same network

**Performance issues**
- Lower FPS in config.py
- Reduce particle effects
- Close other applications

**Audio not working**
- Check system audio settings
- Install audio drivers
- Game will work without audio

### Debug Mode
```bash
python main.py --debug
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit pull request

### Code Style
- Use 4 spaces for indentation
- Follow PEP 8 guidelines
- Add comments for complex logic
- Test on multiple platforms

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Acknowledgments

- **Pygame Community**: For the excellent game development library
- **Classic Pong**: For the timeless gameplay foundation
- **Gaming Community**: For inspiration and feedback

## 🔮 Future Enhancements

- **Online Multiplayer**: Internet-based matchmaking
- **Tournament Mode**: Bracket-style competitions
- **Customization**: Player skins and themes
- **Power-ups**: Additional special abilities
- **AI Opponent**: Single-player mode
- **Replay System**: Record and playback matches
- **Statistics**: Track performance over time

---

**Built with ❤️ for the gaming community**

*Experience the evolution of Pong with Pong Force!*
