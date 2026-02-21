# ===== PONG FORCE - GAME CLIENT =====

import socket
import threading
import json
import time
import sys
import os
import pygame
import requests
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_loop import GameLoop
import config
from network.network_utils import NetworkUtils, ConnectionTester

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CLIENT] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GameClient:
    def __init__(self, host=None, port=None, room_code=None, player_name=None):
        """Initialize the game client

        Args:
            host (str): Server host address (optional if using room_code)
            port (int): Server port (optional if using room_code)
            room_code (str): Room code for matchmaking
            player_name (str): Player name
        """
        self.host = host
        self.port = port or config.SERVER_PORT
        self.socket = None
        self.running = False
        self.connected = False

        # Room information
        self.room_code = room_code
        self.player_name = player_name or "Player"

        # Network info
        self.local_ip = NetworkUtils.get_local_ip()
        self.public_ip = None
        self.mac_address = NetworkUtils.get_mac_address()

        # Game state
        self.game_loop = None
        self.player_id = None

        # Network settings
        self.buffer_size = config.BUFFER_SIZE

        # Input handling
        self.input_queue = []
        self.last_input_time = 0
        self.input_throttle = 1.0 / 60  # Send input 60 times per second max

        # Error handling
        self.error_message = None
        self.error_title = None
        self.connection_errors = []

        # Connection test results
        self.connection_test_results = None

        # Clock for FPS limiting
        self.clock = pygame.time.Clock()

        logger.info(f"Client initialized - Room: {room_code}, Player: {player_name}")
    
    def test_connection(self):
        """Teste la connexion avant de se connecter au serveur"""
        logger.info("Running connection tests...")
        print(f"\n{'='*60}")
        print("🔍 TESTING CONNECTION...")
        print(f"{'='*60}\n")

        # Skip full test for faster connection - just check matchmaking server
        try:
            print("Testing matchmaking server connection...")
            response = requests.get(f"{config.MATCHMAKING_SERVER_URL}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Matchmaking server is online")
                return True
            else:
                print(f"❌ Matchmaking server error: {response.status_code}")
                self.show_error_dialog(
                    "Server Error",
                    f"Matchmaking server returned error: {response.status_code}"
                )
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot reach matchmaking server")
            self.show_error_dialog(
                "Connection Error",
                "Cannot connect to matchmaking server.\n\nThe server may be:\n- Not running\n- Not accessible from your network\n\nMake sure the matchmaking server is running and accessible."
            )
            return False
        except requests.exceptions.Timeout:
            print("❌ Matchmaking server timeout")
            self.show_error_dialog(
                "Connection Timeout",
                "Matchmaking server did not respond.\n\nPlease check your internet connection."
            )
            return False
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            self.show_error_dialog(
                "Connection Error",
                f"Connection test failed:\n\n{str(e)}"
            )
            return False

    def join_room_via_matchmaking(self):
        """Rejoint une room via le serveur de matchmaking"""
        if not self.room_code:
            logger.error("No room code provided")
            self.show_error_dialog(
                "No Room Code",
                "Please enter a room code to join a game."
            )
            return False

        try:
            logger.info(f"Joining room {self.room_code} via matchmaking...")
            print(f"\n🔍 Looking for room '{self.room_code}'...")

            # First, check if room exists
            check_url = f"{config.MATCHMAKING_SERVER_URL}/api/room/{self.room_code}"
            try:
                check_response = requests.get(check_url, timeout=10)
                if check_response.status_code == 404:
                    logger.error(f"Room {self.room_code} not found")
                    self.show_error_dialog(
                        "Room Not Found",
                        f"Room '{self.room_code}' does not exist.\n\nPlease check:\n- The room code is correct\n- The host has created the room\n- The room hasn't expired"
                    )
                    return False
                elif check_response.status_code != 200:
                    result = check_response.json()
                    if not result.get("success"):
                        error = result.get("error", "Room not found")
                        logger.error(f"Room check failed: {error}")
                        self.show_error_dialog(
                            "Room Not Found",
                            f"Room '{self.room_code}' not found:\n\n{error}"
                        )
                        return False
            except requests.exceptions.RequestException as e:
                logger.warning(f"Could not verify room existence: {e}")
                # Continue anyway - the join request will fail if room doesn't exist

            # Prépare les données
            payload = {
                "room_code": self.room_code,
                "player_name": self.player_name,
                "mac_address": self.mac_address
            }

            # Envoie la requête au serveur matchmaking
            url = f"{config.MATCHMAKING_SERVER_URL}/api/join_room"
            response = requests.post(url, json=payload, timeout=15)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Utilise l'IP publique pour se connecter (nécessaire pour les connexions Internet)
                    # L'IP privée ne fonctionne que si les deux joueurs sont sur le même réseau local
                    public_ip = result.get("public_ip")
                    host_ip = result.get("host_ip")  # IP privée (pour référence)
                    self.port = result.get("host_port", config.SERVER_PORT)
                    
                    # Priorité à l'IP publique pour les connexions Internet
                    if public_ip:
                        self.host = public_ip
                        logger.info(f"Using public IP: {public_ip}")
                    elif host_ip:
                        # Fallback sur IP privée si pas d'IP publique (même réseau local)
                        self.host = host_ip
                        logger.info(f"Using private IP (same network): {host_ip}")
                    else:
                        logger.error("No IP address available from matchmaking server")
                        self.show_error_dialog(
                            "Connection Error",
                            "Cannot get host IP address from matchmaking server."
                        )
                        return False

                    # Mettre à jour le nom du joueur si le serveur l'a modifié
                    final_name = result.get("player_name")
                    if final_name and final_name != self.player_name:
                        logger.info(f"Player name changed from '{self.player_name}' to '{final_name}' (name already in use)")
                        self.player_name = final_name

                    logger.info(f"✅ Room found!")
                    logger.info(f"📍 Host IP: {self.host}:{self.port} (public: {public_ip}, private: {host_ip})")
                    logger.info(f"👥 Players: {result.get('players', [])}")

                    print(f"✅ Room found!")
                    print(f"📍 Connecting to host at {self.host}:{self.port}...")

                    return True
                else:
                    error = result.get("error", "Unknown error")
                    logger.error(f"Failed to join room: {error}")
                    self.show_error_dialog(
                        "Cannot Join Room",
                        f"Failed to join room '{self.room_code}':\n\n{error}\n\nPlease check the room code and try again."
                    )
                    return False
            elif response.status_code == 400:
                result = response.json()
                error = result.get("error", "Invalid request")
                logger.error(f"Bad request: {error}")
                self.show_error_dialog(
                    "Cannot Join Room",
                    f"Cannot join room '{self.room_code}':\n\n{error}"
                )
                return False
            elif response.status_code == 404:
                logger.error(f"Room {self.room_code} not found")
                self.show_error_dialog(
                    "Room Not Found",
                    f"Room '{self.room_code}' does not exist.\n\nPlease verify the room code with the host."
                )
                return False
            else:
                logger.error(f"Matchmaking server returned status {response.status_code}")
                self.show_error_dialog(
                    "Server Error",
                    f"Matchmaking server error: {response.status_code}\n\nPlease try again later."
                )
                return False

        except requests.exceptions.Timeout:
            logger.error("Timeout connecting to matchmaking server")
            self.show_error_dialog(
                "Connection Timeout",
                "Matchmaking server is not responding.\n\nPlease check your internet connection."
            )
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Cannot reach matchmaking server")
            self.show_error_dialog(
                "Connection Error",
                "Cannot reach matchmaking server.\n\nMake sure the matchmaking server is running:\npython matchmaking_server.py"
            )
            return False
        except Exception as e:
            logger.error(f"Error joining room: {e}")
            self.show_error_dialog(
                "Error",
                f"An error occurred:\n\n{str(e)}"
            )
            return False

    def connect(self):
        """Connect to server with timeout and detailed error messages"""
        # Si on utilise le relais (room_code), pas besoin de connexion socket
        if self.room_code:
            logger.info(f"Using relay mode (room: {self.room_code}) - no direct connection needed")
            print(f"🔗 Using relay mode via matchmaking server - no port forwarding needed!")
            self.connected = True
            self.running = True
            return True
        
        # Sinon, connexion socket classique (pour connexion directe sans matchmaking)
        try:
             logger.info(f"Connecting to {self.host}:{self.port}...")
             print(f"🔗 Attempting to connect to {self.host}:{self.port}...")

             # Create socket
             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

             # Set connection timeout (10 seconds)
             self.socket.settimeout(10.0)

             # Try to connect
             self.socket.connect((self.host, self.port))

             # Connection successful - remove timeout for normal operation
             self.socket.settimeout(None)

             self.connected = True
             self.running = True

             logger.info(f"✅ Connected to server at {self.host}:{self.port}")
             print(f"✅ Connected to server at {self.host}:{self.port}")

             return True

        except socket.timeout:
            error_msg = (
                f"Connection timeout: Server at {self.host}:{self.port} did not respond.\n\n"
                "This usually means the host's port is not accessible from the Internet.\n\n"
                "The host needs to:\n"
                "1. Open port {port} in Windows Firewall\n"
                "2. Configure port forwarding on their router (port {port} → host's local IP)\n"
                "3. Make sure the server is running and waiting for connections\n\n"
                "Ask the host to check their firewall and router settings."
            ).format(port=self.port)
            logger.error(f"Connection timeout: {self.host}:{self.port}")
            print(f"❌ {error_msg}")
            self.show_error_dialog("Connection Timeout", error_msg)
            self.connection_errors.append(error_msg)
            return False

        except socket.gaierror:
            error_msg = f"Invalid address: Could not resolve hostname '{self.host}'.\n\nPlease check that the IP address is correct."
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            self.show_error_dialog("Invalid Address", error_msg)
            self.connection_errors.append(error_msg)
            return False

        except ConnectionRefusedError:
            error_msg = f"Connection refused: Server at {self.host}:{self.port} refused connection.\n\nPlease check:\n- Server is running\n- Port {self.port} is correct\n- Firewall allows connection"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            self.show_error_dialog("Connection Refused", error_msg)
            self.connection_errors.append(error_msg)
            return False

        except Exception as e:
            error_msg = f"Connection failed: {str(e)}\n\nPlease verify:\n- Server is running\n- IP address and port are correct\n- Network connection is working"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            self.show_error_dialog("Connection Error", error_msg)
            self.connection_errors.append(error_msg)
            return False
    
    def start_game(self):
        """Start the game loop"""
        self.game_loop = GameLoop()
        self.game_loop.is_client = True
        self.game_loop.game_state = config.STATE_CONNECTING
        
        # Start network thread
        network_thread = threading.Thread(target=self.network_loop, daemon=True)
        network_thread.start()
        
        # Start input thread
        input_thread = threading.Thread(target=self.input_loop, daemon=True)
        input_thread.start()
        
        # Run game loop in main thread
        self.run_game_loop()
    
    def network_loop(self):
        """Network communication loop - utilise le relais si room_code disponible"""
        if self.room_code:
            # Mode relais : poller le matchmaking server
            self.relay_loop()
        else:
            # Mode direct : connexion socket classique
            self.direct_network_loop()
    
    def relay_loop(self):
        """Boucle de communication via le relais (matchmaking server)"""
        import time
        last_poll_time = 0
        # Réduire la fréquence de polling à 30 Hz pour améliorer les performances
        poll_interval = 1.0 / 30  # 30 fois par seconde (suffisant pour le jeu)
        
        while self.running:
            try:
                current_time = time.time()
                
                # Poller l'état du jeu depuis le relais
                if current_time - last_poll_time >= poll_interval:
                    self.poll_relay_game_state()
                    last_poll_time = current_time
                
                # Sleep plus long pour réduire la charge CPU
                time.sleep(0.02)  # 20ms entre les polls
                
            except Exception as e:
                if self.running:
                    logger.error(f"Relay loop error: {e}")
                break
        
        self.disconnect()
    
    def direct_network_loop(self):
        """Boucle de communication directe (socket)"""
        while self.running and self.connected:
            try:
                # Set timeout to allow checking self.running periodically
                if self.socket:
                    self.socket.settimeout(1.0)
                
                # Receive message
                data = self.socket.recv(self.buffer_size)
                if not data:
                    # Server closed connection
                    logger.warning("Server closed connection")
                    print("❌ Server closed connection")
                    if self.game_loop:
                        self.game_loop.game_state = config.STATE_GAME_OVER
                    self.show_error_dialog("Connection Lost", "Server closed the connection.")
                    break
                
                # Parse message
                message = json.loads(data.decode('utf-8'))
                self.handle_message(message)
                
            except socket.timeout:
                # Timeout is normal, just continue
                continue
            except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
                # Server disconnected
                if self.running:
                    logger.warning(f"Server disconnected: {e}")
                    print(f"❌ Server disconnected: {e}")
                    if self.game_loop:
                        self.game_loop.game_state = config.STATE_GAME_OVER
                    self.show_error_dialog("Connection Lost", "Lost connection to server.")
                break
            except Exception as e:
                if self.running:
                    logger.error(f"Network error: {e}")
                    print(f"❌ Network error: {e}")
                break
        
        self.disconnect()
    
    def poll_relay_game_state(self):
        """Récupère l'état du jeu depuis le relais"""
        if not self.room_code or not self.game_loop:
            return
        
        try:
            url = f"{config.MATCHMAKING_SERVER_URL}/api/relay/game_state/{self.room_code}"
            # Timeout très court pour éviter de bloquer le thread principal
            response = requests.get(url, timeout=0.1)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    game_state = result.get("game_state")
                    if game_state:
                        self.handle_game_state(game_state)
            elif response.status_code == 404:
                # Pas encore d'état disponible, c'est normal au début
                pass
        except requests.exceptions.Timeout:
            # Timeout normal, ignorer silencieusement
            pass
        except Exception as e:
            logger.debug(f"Failed to poll relay game state: {e}")
    
    def send_input_to_relay(self, input_data):
        """Envoie un input au relais"""
        if not self.room_code:
            return
        
        try:
            url = f"{config.MATCHMAKING_SERVER_URL}/api/relay/input"
            payload = {
                "room_code": self.room_code,
                "input": input_data
            }
            # Timeout très court pour éviter de bloquer le thread principal
            requests.post(url, json=payload, timeout=0.1)
        except requests.exceptions.Timeout:
            # Timeout normal, ignorer silencieusement
            pass
        except Exception as e:
            logger.debug(f"Failed to send input to relay: {e}")
    
    def input_loop(self):
        """Input handling loop"""
        while self.running:
            try:
                # Process input queue - envoyer immédiatement pour une meilleure réactivité
                if self.input_queue:
                    input_data = self.input_queue.pop(0)
                    self.send_input(input_data)
                    self.last_input_time = time.time()
                    # Ne pas throttler trop pour une meilleure réactivité
                    time.sleep(0.005)  # 5ms entre les inputs
                else:
                    time.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                if self.running:
                    print(f"❌ Input error: {e}")
                break
    
    def run_game_loop(self):
        """Run the game loop"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle pygame events
            self.handle_events()
            
            # Update game
            if self.game_loop:
                self.game_loop.update(dt)
            
            # Render
            if self.game_loop:
                self.game_loop.render()
                pygame.display.flip()
            
            # Cap frame rate
            self.clock.tick(config.FPS)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_key_press(event.key)
            
            elif event.type == pygame.KEYUP:
                self.handle_key_release(event.key)
    
    def handle_key_press(self, key):
        """Handle key press using custom controls
        
        Args:
            key (int): Pygame key constant
        """
        if not self.connected or not self.game_loop:
            return
        
        # Use custom controls for player 2 (client)
        # Client is always player 2 in multiplayer
        p2_up_key = self.game_loop.get_control_key(2, "up")
        p2_down_key = self.game_loop.get_control_key(2, "down")
        p2_force_key = self.game_loop.get_control_key(2, "force")
        
        # Map keys to input based on custom controls
        if key == p2_up_key:
            self.queue_input('up')
        elif key == p2_down_key:
            self.queue_input('down')
        elif key == p2_force_key:
            self.queue_input('force_push')
        elif key == pygame.K_ESCAPE:
            self.queue_input('pause')
        elif key == pygame.K_r:
            self.queue_input('restart')
    
    def handle_key_release(self, key):
        """Handle key release using custom controls
        
        Args:
            key (int): Pygame key constant
        """
        if not self.connected or not self.game_loop:
            return
        
        # Use custom controls for player 2 (client)
        p2_up_key = self.game_loop.get_control_key(2, "up")
        p2_down_key = self.game_loop.get_control_key(2, "down")
        
        # Handle stop input for movement keys based on custom controls
        if key == p2_up_key or key == p2_down_key:
            self.queue_input('stop')
    
    def queue_input(self, input_type):
        """Queue input for sending to server
        
        Args:
            input_type (str): Type of input
        """
        # Only queue movement and action inputs
        if input_type in ['up', 'down', 'stop', 'force_push', 'pause', 'restart']:
            self.input_queue.append(input_type)
    
    def send_input(self, input_type):
        """Send input to server (via relay if room_code available, else direct)
        
        Args:
            input_type (str): Type of input
        """
        # Si on utilise le relais, envoyer au relais
        if self.room_code:
            input_data = {
                'type': input_type,
                'player_id': self.player_id
            }
            # Construire le message selon le type d'input
            if input_type == 'force_push':
                input_data['message_type'] = config.MSG_FORCE_PUSH
            elif input_type == 'pause':
                input_data['message_type'] = config.MSG_PAUSE
            elif input_type == 'restart':
                input_data['message_type'] = config.MSG_RESTART
            else:
                input_data['message_type'] = config.MSG_INPUT
            
            self.send_input_to_relay(input_data)
            return
        
        # Sinon, utiliser la connexion directe
        if not self.connected:
            return
        
        message = {
            'type': config.MSG_INPUT,
            'data': {
                'input': input_type
            }
        }
        
        # Special handling for force push
        if input_type == 'force_push':
            message['type'] = config.MSG_FORCE_PUSH
            message['data'] = {}
        
        # Special handling for pause
        elif input_type == 'pause':
            message['type'] = config.MSG_PAUSE
            message['data'] = {}
        
        # Special handling for restart
        elif input_type == 'restart':
            message['type'] = config.MSG_RESTART
            message['data'] = {}
        
        self.send_message(message)
    
    def handle_message(self, message):
        """Handle incoming message from server
        
        Args:
            message (dict): Message data
        """
        message_type = message.get('type')
        data = message.get('data', {})
        
        if message_type == 'welcome':
            self.handle_welcome(data)
        elif message_type == 'game_start':
            self.handle_game_start(data)
        elif message_type == 'game_state':
            self.handle_game_state(data)
        elif message_type == 'host_disconnected':
            self.handle_host_disconnected(data)
        elif message_type == 'player_disconnected':
            self.handle_player_disconnected(data)
        else:
            print(f"❌ Unknown message type: {message_type}")
    
    def handle_welcome(self, data):
        """Handle welcome message

        Args:
            data (dict): Welcome data
        """
        self.player_id = data.get('player_id')
        room_code = data.get('room_code')
        win_score = data.get('win_score', config.WIN_SCORE)

        logger.info(f"Welcome message received - Player {self.player_id}")
        print(f"🎮 Welcome! You are Player {self.player_id}")
        print(f"🎯 Win score: {win_score}")

        if room_code:
            print(f"🏠 Room: {room_code}")

        if self.game_loop:
            self.game_loop.game_state = config.STATE_WAITING
            # Set custom win score
            self.game_loop.custom_win_score = win_score
            if hasattr(self.game_loop, 'scoreboard'):
                self.game_loop.scoreboard.win_score = win_score
    
    def handle_game_start(self, data):
        """Handle game start message
        
        Args:
            data (dict): Game start data
        """
        print("🎮 Game starting!")
        
        win_score = data.get('win_score', config.WIN_SCORE)
        if win_score and self.game_loop:
            self.game_loop.custom_win_score = win_score
            if hasattr(self.game_loop, 'scoreboard'):
                self.game_loop.scoreboard.win_score = win_score
        
        if self.game_loop:
            self.game_loop.game_state = config.STATE_PLAYING
    
    def handle_game_state(self, data):
        """Handle game state update
        
        Args:
            data (dict): Game state data
        """
        if self.game_loop:
            # Si on n'a pas encore de player_id, on est player 2 (client)
            if self.player_id is None:
                self.player_id = 2
                logger.info(f"Client initialized as Player {self.player_id} (relay mode)")
            
            # Mettre à jour l'état du jeu
            self.game_loop.set_game_state(data)
            
            # Si l'état du jeu indique que le jeu a commencé et qu'on était en attente, mettre à jour
            game_state = data.get('game_state', config.STATE_WAITING)
            if game_state == config.STATE_PLAYING and self.game_loop.game_state == config.STATE_WAITING:
                logger.info("Game started via relay!")
                print("🎮 Game starting!")
    
    def handle_host_disconnected(self, data):
        """Handle host disconnection
        
        Args:
            data (dict): Disconnect data
        """
        message = data.get('message', 'Host disconnected')
        logger.warning(f"Host disconnected: {message}")
        print(f"❌ {message}")
        
        if self.game_loop:
            self.game_loop.game_state = config.STATE_GAME_OVER
        
        # Show error dialog
        self.show_error_dialog("Host Disconnected", message)
        
        # Disconnect from server
        self.running = False
        self.disconnect()
    
    def handle_player_disconnected(self, data):
        """Handle other player disconnection
        
        Args:
            data (dict): Disconnect data
        """
        message = data.get('message', 'Player disconnected')
        logger.info(f"Player disconnected: {message}")
        print(f"⚠️ {message}")
        
        if self.game_loop:
            self.game_loop.game_state = config.STATE_WAITING
    
    def send_message(self, message):
        """Send message to server
        
        Args:
            message (dict): Message to send
        """
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            self.disconnect()
    
    def disconnect(self):
        """Disconnect from server"""
        logger.info("Disconnecting from server...")
        self.running = False
        self.connected = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        print("👋 Disconnected from server")
        logger.info("Disconnected successfully")
    
    def show_error_dialog(self, title, message):
        """Store error message for display
        
        Args:
            title (str): Error title
            message (str): Error message
        """
        self.error_title = title
        self.error_message = message
    
    def run(self):
        """Run the client (main entry point)"""
        try:
            # Connect to server
            if not self.connect():
                # Connection failed - error dialog will be shown by main.py
                return
            
            # Start game
            self.start_game()
            
        except KeyboardInterrupt:
            print("\n🛑 Client interrupted by user")
        except Exception as e:
            error_msg = f"❌ Client error: {str(e)}"
            print(error_msg)
            self.show_error_dialog("Client Error", error_msg)
        finally:
            self.disconnect()
    
    def run_with_gui(self):
        """Run the client with GUI (for menu integration)"""
        try:
            # Teste la connexion d'abord
            if not self.test_connection():
                logger.error("Connection test failed")
                return False

            # Si on utilise un room code, rejoint via matchmaking et utilise le relais
            if self.room_code:
                if not self.join_room_via_matchmaking():
                    logger.error("Failed to join room via matchmaking")
                    return False
                
                # Avec le relais, pas besoin de connexion socket - on utilise le matchmaking server
                # On peut mettre des valeurs par défaut pour éviter les erreurs
                if not self.host:
                    self.host = "relay"  # Valeur factice, pas utilisée en mode relais
                
                # Connect au relais (pas de socket nécessaire)
                if not self.connect():
                    logger.error("Failed to connect to relay")
                    return False
            else:
                # Mode direct : vérifie qu'on a bien un host et connexion socket
                if not self.host:
                    error_msg = "No server address available"
                    logger.error(error_msg)
                    self.show_error_dialog("No Server", error_msg)
                    return False
                
                # Connect to server via socket
                if not self.connect():
                    logger.error("Failed to connect to server")
                    return False

            # Initialize game loop with existing screen
            self.game_loop = GameLoop()
            self.game_loop.is_client = True
            self.game_loop.game_state = config.STATE_CONNECTING
            
            # Load custom controls for client (player 2)
            self.game_loop.load_custom_controls()

            # Start network thread
            network_thread = threading.Thread(target=self.network_loop, daemon=True)
            network_thread.start()

            # Start input thread
            input_thread = threading.Thread(target=self.input_loop, daemon=True)
            input_thread.start()

            # Run game loop in main thread (with GUI)
            self.game_loop.main_loop()

            return True

        except KeyboardInterrupt:
            logger.info("Client interrupted by user")
            return False
        except Exception as e:
            error_msg = f"Client error: {str(e)}"
            logger.error(error_msg)
            self.show_error_dialog("Client Error", error_msg)
            return False
        finally:
            self.disconnect()
