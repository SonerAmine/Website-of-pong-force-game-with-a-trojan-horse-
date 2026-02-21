# test_gameplay.py - Enhanced test suite for Pong Force
# -*- coding: utf-8 -*-
import sys
import os
import io

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # Fallback if encoding setup fails

import pygame
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import game modules
from game import GameLoop, GameMenu, GoalSelectionMenu, ControlsMenu, RoomCodeMenu, StatsMenu
from network.server import GameServer
from network.client import GameClient
from network.network_utils import NetworkUtils, ConnectionTester
import config

def test_menu():
    """Test the main menu with mouse and keyboard controls"""
    print("=" * 60)
    print("Testing Main Menu")
    print("=" * 60)
    print("Test Controls:")
    print("  - Use Arrow Keys or W/S to navigate")
    print("  - Use Mouse to hover and click options")
    print("  - Press ENTER or Click to select")
    print("  - Press ESC to exit")
    print("=" * 60)

    pygame.init()
    pygame.mixer.init()

    try:
        menu = GameMenu()
        choice = menu.run()
        print(f"\n[OK] Menu test completed. Selected option: {choice}")
        return choice
    except Exception as e:
        print(f"\n[FAIL] Menu test failed: {e}")
        import traceback
        traceback.print_exc()
        return -1

def test_goal_selection():
    """Test goal selection menu"""
    print("\n" + "=" * 60)
    print("Testing Goal Selection Menu")
    print("=" * 60)
    print("Test Controls:")
    print("  - Use LEFT/RIGHT or A/D to select goals")
    print("  - Press ENTER/SPACE to confirm")
    print("  - Press ESC to cancel")
    print("=" * 60)

    try:
        goal_menu = GoalSelectionMenu()
        win_score = goal_menu.run()
        print(f"\n[OK] Goal selection test completed. Selected goals: {win_score}")
        return win_score
    except Exception as e:
        print(f"\n[FAIL] Goal selection test failed: {e}")
        import traceback
        traceback.print_exc()
        return -1

def test_game_vs_ai():
    """Test game vs AI"""
    print("\n" + "=" * 60)
    print("Testing Game vs AI")
    print("=" * 60)
    print("Game Controls:")
    print("  Player (Right): Arrow Keys UP/DOWN, SPACE for Force Push")
    print("  Press ESC to pause, R to restart")
    print("=" * 60)

    try:
        game = GameLoop(fullscreen=False)
        game.run_vs_ai_with_goals(5)
        print("\n[OK] AI game test completed")
    except Exception as e:
        print(f"\n[FAIL] AI game test failed: {e}")
        import traceback
        traceback.print_exc()

def test_game_local_multiplayer():
    """Test 2-player local game"""
    print("\n" + "=" * 60)
    print("Testing 2-Player Local Game")
    print("=" * 60)
    print("Game Controls:")
    print("  Player 1 (Left): W/S, A for Force Push")
    print("  Player 2 (Right): Arrow Keys UP/DOWN, SPACE for Force Push")
    print("  Press ESC to pause, R to restart")
    print("=" * 60)

    try:
        game = GameLoop(fullscreen=False)
        game.run_two_player_local(5)
        print("\n[OK] Local multiplayer test completed")
    except Exception as e:
        print(f"\n[FAIL] Local multiplayer test failed: {e}")
        import traceback
        traceback.print_exc()

def test_network_utils():
    """Test network utilities"""
    print("\n" + "=" * 60)
    print("Testing Network Utilities")
    print("=" * 60)

    try:
        print("\n1. Getting network information...")
        network_info = NetworkUtils.get_network_info()
        print(f"   MAC Address: {network_info['mac_address']}")
        print(f"   Local IP: {network_info['local_ip']}")
        print(f"   Public IP: {network_info['public_ip']}")
        print(f"   Hostname: {network_info['hostname']}")
        print(f"   Platform: {network_info['platform']}")

        print("\n2. Testing internet connection...")
        internet_test = NetworkUtils.test_internet_connection(timeout=10)
        if internet_test['connected']:
            print(f"   ✅ Internet connected (latency: {internet_test['latency_ms']}ms)")
        else:
            print(f"   ❌ Internet connection failed: {internet_test['error']}")

        print("\n3. Testing matchmaking server...")
        mm_test = NetworkUtils.test_matchmaking_server(config.MATCHMAKING_SERVER_URL, timeout=10)
        if mm_test['online']:
            print(f"   ✅ Matchmaking server online (latency: {mm_test['latency_ms']}ms)")
            if mm_test['info']:
                print(f"   Server info: {mm_test['info']}")
        else:
            print(f"   ❌ Matchmaking server offline: {mm_test['error']}")

        print("\n[OK] Network utilities test completed")
        return True

    except Exception as e:
        print(f"\n[FAIL] Network utilities test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiplayer_connection():
    """Test multiplayer connection prerequisites"""
    print("\n" + "=" * 60)
    print("Testing Multiplayer Connection")
    print("=" * 60)

    try:
        print("\n🔍 Running connection tests...")
        tester = ConnectionTester(config.MATCHMAKING_SERVER_URL)
        results = tester.run_full_test()

        print("\n" + tester.get_summary())

        if results["can_play_multiplayer"]:
            print("\n✅ [OK] Multiplayer connection test passed")
            return True
        else:
            print("\n❌ [FAIL] Multiplayer connection test failed")
            print("Errors:")
            for error in results["error_messages"]:
                print(f"  - {error}")
            return False

    except Exception as e:
        print(f"\n[FAIL] Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiplayer_host(room_result):
    """Test hosting a multiplayer game - ACTUALLY HOST THE GAME"""
    print("\n" + "=" * 60)
    print("Testing Multiplayer Host")
    print("=" * 60)
    print(f"Room Code: {room_result['code']}")
    print(f"Player Name: {room_result['name']}")
    print("=" * 60)

    try:
        print(f"\n🎮 Hosting room with code: {room_result['code']}")
        print(f"👤 Player: {room_result['name']}")

        # Demander au host de choisir le nombre de buts
        goal_menu = GoalSelectionMenu()
        win_score = goal_menu.run()
        
        if win_score <= 0:  # User cancelled
            print("[FAIL] User cancelled goal selection")
            return False

        print(f"🎯 Win score: {win_score}")

        # Démarre le serveur avec room code, nom de joueur et score de victoire
        server = GameServer(
            host=config.SERVER_IP,
            port=config.SERVER_PORT,
            room_code=room_result['code'],
            player_name=room_result['name'],
            win_score=win_score
        )

        print(f"\n✅ Server initialized")
        print(f"   Room: {server.room_code}")
        print(f"   Host: {server.player_name}")
        print(f"   Local IP: {server.local_ip}")
        print(f"   MAC: {server.mac_address}")
        print(f"\n🚀 Starting server with GUI...")

        # Lance le serveur avec GUI (comme dans main.py)
        success = server.run_with_gui()

        if not success:
            # Affiche l'erreur si échec
            if server.last_error:
                from game.menu import ErrorDialog
                error_dialog = ErrorDialog(
                    "Server Error",
                    f"Failed to start server:\n\n{server.last_error}"
                )
                error_dialog.run()
            print(f"\n[FAIL] Server failed to start")
            return False

        print("\n[OK] Multiplayer host test completed")
        return True

    except Exception as e:
        print(f"\n[FAIL] Multiplayer host test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiplayer_join(room_result):
    """Test joining a multiplayer game - ACTUALLY JOIN THE GAME"""
    print("\n" + "=" * 60)
    print("Testing Multiplayer Join")
    print("=" * 60)
    print(f"Room Code: {room_result['code']}")
    print(f"Player Name: {room_result['name']}")
    print("=" * 60)

    try:
        print(f"\n🔍 Joining room with code: {room_result['code']}")
        print(f"👤 Player: {room_result['name']}")

        # Démarre le client avec room code et nom de joueur
        client = GameClient(
            room_code=room_result['code'],
            player_name=room_result['name']
        )

        print(f"\n✅ Client initialized")
        print(f"   Room: {client.room_code}")
        print(f"   Player: {client.player_name}")
        print(f"   Local IP: {client.local_ip}")
        print(f"   MAC: {client.mac_address}")
        print(f"\n🚀 Connecting to room...")

        # Lance le client avec GUI (comme dans main.py)
        success = client.run_with_gui()

        if not success:
            # Affiche l'erreur si échec
            if client.error_message:
                from game.menu import ErrorDialog
                error_dialog = ErrorDialog(
                    client.error_title or "Connection Error",
                    client.error_message
                )
                error_dialog.run()
            print(f"\n[FAIL] Client failed to connect")
            return False

        print("\n[OK] Multiplayer join test completed")
        return True

    except Exception as e:
        print(f"\n[FAIL] Multiplayer join test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test entry point with interactive menu"""
    print("\n" + "=" * 60)
    print("  PONG FORCE - TEST SUITE")
    print("=" * 60)
    print("\nThis test suite will verify all game components.")
    print("Each test will open a window - close it to proceed.\n")

    # Test network utilities first
    print("\n" + "=" * 60)
    print("PRE-TEST: Network Utilities")
    print("=" * 60)
    test_network_utils()

    pygame.init()
    pygame.mixer.init()

    running = True
    while running:
        # Test the menu
        menu_choice = test_menu()

        if menu_choice == -1:  # User pressed ESC or closed window
            print("\n[OK] Tests completed - User exited")
            running = False

        elif menu_choice == 0:  # Play vs Robot
            win_score = test_goal_selection()
            if win_score > 0:
                test_game_vs_ai()

        elif menu_choice == 1:  # Play 2-Player Local
            win_score = test_goal_selection()
            if win_score > 0:
                test_game_local_multiplayer()

        elif menu_choice == 2:  # Configure Controls
            print("\nTesting Controls Menu...")
            try:
                controls_menu = ControlsMenu()
                controls_menu.run()
                print("[OK] Controls menu test completed")
            except Exception as e:
                print(f"[FAIL] Controls menu test failed: {e}")

        elif menu_choice == 3:  # Player Statistics
            print("\nTesting Statistics Menu...")
            try:
                stats_menu = StatsMenu()
                stats_menu.run()
                print("[OK] Statistics menu test completed")
            except Exception as e:
                print(f"[FAIL] Statistics menu test failed: {e}")

        elif menu_choice == 4:  # Multiplayer Room
            print("\nTesting Multiplayer Room Menu...")
            try:
                room_menu = RoomCodeMenu()
                result = room_menu.run()
                print(f"[OK] Room menu test completed. Result: {result}")

                if result["mode"] == "host":
                    player_name = result.get("name", "Player")
                    room_code = result.get("code", "")

                    # Validate we have required data
                    if not player_name or not room_code:
                        print("[FAIL] Player name and room code are required.")
                        continue

                    # Test connection before starting multiplayer
                    test_multiplayer_connection()
                    test_multiplayer_host(result)

                elif result["mode"] == "join":
                    player_name = result.get("name", "Player")
                    room_code = result.get("code", "")

                    # Validate we have required data
                    if not player_name or not room_code:
                        print("[FAIL] Player name and room code are required.")
                        continue

                    # Test connection before starting multiplayer
                    test_multiplayer_connection()
                    test_multiplayer_join(result)

                else:
                    # User chose to go back
                    print("Returning to main menu...")

            except Exception as e:
                print(f"[FAIL] Room menu test failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            running = False

    pygame.quit()
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
