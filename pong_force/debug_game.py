# debug_game.py - Debug actual game execution
import pygame
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath('__file__')))

def main():
    """Debug actual game execution"""
    print("=== DEBUGGING ACTUAL GAME EXECUTION ===")
    
    pygame.init()
    
    try:
        # Test the exact same flow as main.py
        from game.menu import GameMenu, GoalSelectionMenu
        from game.game_loop import GameLoop
        
        print("1. Creating GameMenu...")
        menu = GameMenu()
        print("2. Simulating menu choice 0 (vs AI)...")
        
        # Test goal selection
        goal_menu = GoalSelectionMenu()
        print("3. Testing goal selection menu...")
        win_score = goal_menu.run()
        print(f"   - Goal selection returned: {win_score}")
        
        if win_score > 0:
            print("4. Creating GameLoop...")
            game = GameLoop()
            print("5. Calling load_custom_controls...")
            game.load_custom_controls()
            print("6. Checking loaded controls...")
            p1_controls = game.custom_controls.get('player1', {}).get('vs_robot', {})
            print(f"   - Player 1 vs_robot controls: {p1_controls}")
            
            print("7. Starting game loop (will exit on DELETE)...")
            
            # Run game loop with DELETE key detection
            start_time = pygame.time.get_ticks()
            
            while game.running and pygame.time.get_ticks() - start_time < 5000:  # 5 seconds max
                game.handle_events()
                
                # Check if DELETE key was pressed
                if pygame.K_DELETE in game.keys_just_pressed:
                    print("   - DELETE key detected! Exiting...")
                    game.running = False
                    break
                
                pygame.display.flip()
                game.clock.tick(60)
            
            if not game.running:
                print("8. Game exited successfully via DELETE key")
            else:
                print("8. Game did not exit (DELETE key not detected)")
        
    except Exception as e:
        print(f"Error: {e}")
        
    pygame.quit()

if __name__ == "__main__":
    main()
