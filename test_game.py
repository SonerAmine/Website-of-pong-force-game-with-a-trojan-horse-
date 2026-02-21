#!/usr/bin/env python3
"""
Quick test script to verify the Pong Force game works
Run this to test the game before building the executable
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import pygame
        print(f"✅ Pygame {pygame.version.ver} imported successfully")
    except ImportError as e:
        print(f"❌ Pygame import failed: {e}")
        print("   Install with: pip install pygame")
        return False
    
    # Test game modules
    sys.path.append('pong_force')
    
    try:
        from pong_force.config import *
        print("✅ Config module imported")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from pong_force.game.paddle import Paddle
        print("✅ Paddle class imported")
    except ImportError as e:
        print(f"❌ Paddle import failed: {e}")
        return False
    
    try:
        from pong_force.game.ball import Ball
        print("✅ Ball class imported")
    except ImportError as e:
        print(f"❌ Ball import failed: {e}")
        return False
    
    try:
        from pong_force.game.game_loop import GameLoop
        print("✅ GameLoop class imported")
    except ImportError as e:
        print(f"❌ GameLoop import failed: {e}")
        return False
    
    return True

def test_game_creation():
    """Test if game objects can be created"""
    print("\n🎮 Testing game object creation...")
    
    try:
        from pong_force.game.paddle import Paddle
        from pong_force.game.ball import Ball
        
        # Test paddle creation
        paddle = Paddle(100, 200, 1, (0, 255, 255))
        print("✅ Paddle created successfully")
        
        # Test ball creation
        ball = Ball(400, 300)
        print("✅ Ball created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Game object creation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎮 Pong Force - Game Test")
    print("=" * 30)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please fix the issues above.")
        return False
    
    # Test game creation
    if not test_game_creation():
        print("\n❌ Game creation tests failed. Please fix the issues above.")
        return False
    
    print("\n🎉 All tests passed!")
    print("\n✅ Your game is ready to play!")
    print("\n🚀 To play the game:")
    print("   1. Run: python pong_force/main.py")
    print("   2. Or build executable: python setup_download.bat")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
