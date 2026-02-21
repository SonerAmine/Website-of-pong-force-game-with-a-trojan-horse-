# ===== PONG FORCE - GAME SERVER =====

import socket
import threading
import json
import time
import sys
import os
import requests
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game_loop import GameLoop
import config
from network.network_utils import NetworkUtils

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SERVER] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GameServer:
    def __init__(self, host, port, room_code=None, player_name=None, win_score=None):
        """Initialize the game server

        Args:
            host (str): Server host address
            port (int): Server port
            room_code (str): Room code for matchmaking
            player_name (str): Host player name
            win_score (int): Number of goals needed to win (default: config.WIN_SCORE)
        """
        self.host = host
        self.port = port
        self.socket = None
        self.clients = []
        self.running = False

        # Room information
        self.room_code = room_code
        self.player_name = player_name or "Host"
        self.win_score = win_score or config.WIN_SCORE
        self.registered_with_matchmaking = False

        # Network info
        self.local_ip = NetworkUtils.get_local_ip()
        self.public_ip = None
        self.mac_address = NetworkUtils.get_mac_address()

        # Game state
        self.game_loop = None
        self.game_thread = None

        # Network settings
        self.max_clients = 1  # Only 1 client needed (host is player 1, client is player 2)
        self.buffer_size = config.BUFFER_SIZE
        self.update_rate = config.NETWORK_UPDATE_RATE

        # Error tracking
        self.last_error = None
        self.connection_errors = []

        # Message handling
        self.message_handlers = {
            config.MSG_CONNECT: self.handle_connect,
            config.MSG_DISCONNECT: self.handle_disconnect,
            config.MSG_INPUT: self.handle_input,
            config.MSG_FORCE_PUSH: self.handle_force_push,
            config.MSG_PAUSE: self.handle_pause,
            config.MSG_RESTART: self.handle_restart
        }

        logger.info(f"Server initialized - Room: {room_code}, Host: {player_name}")
    
    def register_with_matchmaking(self):
        """Enregistre le serveur avec le serveur de matchmaking"""
        if not self.room_code:
            logger.warning("No room code provided, skipping matchmaking registration")
            return False

        try:
            logger.info(f"Registering room {self.room_code} with matchmaking server...")

            # Obtient l'IP publique
            self.public_ip = NetworkUtils.get_public_ip(timeout=10)

            if not self.public_ip:
                logger.error("Failed to obtain public IP")
                self.last_error = "Cannot obtain public IP address"
                return False

            # Prépare les données
            # Envoie l'IP publique ET l'IP locale
            # Le matchmaking server utilisera l'IP publique pour les connexions Internet
            payload = {
                "room_code": self.room_code,
                "player_name": self.player_name,
                "mac_address": self.mac_address,
                "host_ip": self.local_ip,  # IP privée (pour référence, si même réseau local)
                "host_port": self.port,
                "public_ip": self.public_ip  # IP publique (pour connexions Internet)
            }

            # Envoie la requête au serveur matchmaking
            url = f"{config.MATCHMAKING_SERVER_URL}/api/create_room"
            response = requests.post(url, json=payload, timeout=15)

            if response.status_code in [200, 201]:
                result = response.json()
                if result.get("success"):
                    self.registered_with_matchmaking = True
                    logger.info(f"✅ Room {self.room_code} registered successfully!")
                    logger.info(f"📍 Public IP: {self.public_ip}")
                    logger.info(f"🏠 Local IP: {self.local_ip}")
                    logger.info(f"🔑 MAC Address: {self.mac_address}")
                    return True
                else:
                    error = result.get("error", "Unknown error")
                    logger.error(f"Matchmaking registration failed: {error}")
                    self.last_error = error
                    return False
            else:
                logger.error(f"Matchmaking server returned status {response.status_code}")
                self.last_error = f"Server error: {response.status_code}"
                return False

        except requests.exceptions.Timeout:
            logger.error("Timeout connecting to matchmaking server")
            self.last_error = "Matchmaking server timeout"
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Cannot reach matchmaking server")
            self.last_error = "Cannot reach matchmaking server"
            return False
        except Exception as e:
            logger.error(f"Matchmaking registration error: {e}")
            self.last_error = str(e)
            return False

    def update_room_status(self, status):
        """Met à jour le statut de la room sur le serveur matchmaking"""
        if not self.registered_with_matchmaking or not self.room_code:
            return

        try:
            payload = {
                "room_code": self.room_code,
                "status": status
            }

            url = f"{config.MATCHMAKING_SERVER_URL}/api/update_room"
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"Room status updated to: {status}")
            else:
                logger.warning(f"Failed to update room status: {response.status_code}")

        except Exception as e:
            logger.warning(f"Error updating room status: {e}")

    def close_room(self):
        """Ferme la room sur le serveur matchmaking"""
        if not self.registered_with_matchmaking or not self.room_code:
            return

        try:
            payload = {"room_code": self.room_code}
            url = f"{config.MATCHMAKING_SERVER_URL}/api/close_room"
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"Room {self.room_code} closed on matchmaking server")
            else:
                logger.warning(f"Failed to close room: {response.status_code}")

        except Exception as e:
            logger.warning(f"Error closing room: {e}")

    def start(self):
        """Start the server with improved error handling"""
        try:
            # Enregistre avec le serveur matchmaking si room_code fourni
            if self.room_code:
                if not self.register_with_matchmaking():
                    print(f"\n❌ Failed to register with matchmaking server")
                    print(f"Error: {self.last_error}")
                    print(f"\n💡 Make sure the matchmaking server is running:")
                    print(f"   python matchmaking_server.py")
                    input("\nPress Enter to exit...")
                    return

            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                self.socket.bind((self.host, self.port))
            except OSError as e:
                if e.errno == 10048:  # Port already in use on Windows
                    print(f"❌ Port {self.port} is already in use!")
                    print(f"💡 Close other instances of Pong Force or use a different port")
                    self.last_error = f"Port {self.port} already in use"
                    input("Press Enter to exit...")
                    return
                else:
                    raise

            self.socket.listen(self.max_clients)

            self.running = True
            print(f"\n{'='*60}")
            print(f"✅ SERVER STARTED SUCCESSFULLY!")
            print(f"{'='*60}")

            if self.room_code:
                print(f"🎮 Room Code: {self.room_code}")
                print(f"👤 Host: {self.player_name}")
                print(f"📍 Public IP: {self.public_ip}")
                print(f"🏠 Local IP: {self.local_ip}:{self.port}")
                print(f"🔑 MAC: {self.mac_address}")
                print(f"\n💡 Share room code '{self.room_code}' with your opponent!")
                print(f"\n⚠️  IMPORTANT: For Internet play, you need to:")
                print(f"   1. Open port {self.port} in Windows Firewall")
                print(f"   2. Configure port forwarding on your router:")
                print(f"      - External Port: {self.port}")
                print(f"      - Internal IP: {self.local_ip}")
                print(f"      - Internal Port: {self.port}")
                print(f"   3. Protocol: TCP")
            else:
                print(f"📍 Listening on {self.host}:{self.port}")
                print(f"🌐 Share your PUBLIC IP with other players")
                print(f"💡 Find your IP at: www.whatismyip.com")

            print(f"\n⏳ Waiting for {self.max_clients} player(s) to connect...")
            print(f"{'='*60}\n")

            # Start game loop
            self.start_game()

            # Start accepting connections
            self.accept_connections()

        except KeyboardInterrupt:
            print("\n🛑 Server interrupted by user")
            self.stop()
        except Exception as e:
            logger.error(f"Server error: {e}")
            print(f"❌ Server error: {e}")
            import traceback
            traceback.print_exc()
            self.last_error = str(e)
            self.connection_errors.append(str(e))
            input("Press Enter to exit...")
            self.stop()
    
    def start_game(self):
        """Start the game loop"""
        # Use existing pygame screen instead of creating a new one
        self.game_loop = GameLoop()
        self.game_loop.is_server = True
        self.game_loop.game_state = config.STATE_WAITING
        
        # Load custom controls for host (player 1)
        self.game_loop.load_custom_controls()
        
        # Set custom win score
        self.game_loop.custom_win_score = self.win_score
        if hasattr(self.game_loop, 'scoreboard'):
            self.game_loop.scoreboard.win_score = self.win_score
        
        # Don't start game thread yet - will be started in run_with_gui()
        self.game_thread = None
    
    def run_game_loop(self):
        """Run the game loop (in separate thread) - DEPRECATED, use run_game_loop_main instead"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Update game
            self.game_loop.update(dt)
            
            # Send game state to clients
            self.broadcast_game_state()
            
            # Cap update rate
            time.sleep(1.0 / self.update_rate)
    
    
    def accept_connections(self):
        """Accept client connections"""
        print("⏳ Waiting for players to connect...")
        
        while self.running:
            try:
                # Accept connection
                client_socket, address = self.socket.accept()
                print(f"🔗 Client connected from {address}")
                
                # Check if we have room for more clients
                if len(self.clients) >= self.max_clients:
                    print(f"❌ Server full, rejecting connection from {address}")
                    client_socket.close()
                    continue
                
                # Create client handler
                client_handler = ClientHandler(client_socket, address, self)
                self.clients.append(client_handler)
                
                # Start client handler thread
                client_thread = threading.Thread(target=client_handler.run, daemon=True)
                client_thread.start()
                
                # Start game if we have enough players
                if len(self.clients) == self.max_clients:
                    self.start_game_session()
                
            except Exception as e:
                if self.running:
                    print(f"❌ Connection error: {e}")
                break
    
    def start_game_session(self):
        """Start the game session"""
        logger.info("Starting game session with 2 players!")
        print("🎮 Starting game session with 2 players!")

        self.game_loop.game_state = config.STATE_PLAYING

        # Met à jour le statut de la room
        self.update_room_status("in_progress")

        # Send game start message to all clients with win score
        message = {
            'type': 'game_start',
            'data': {
                'message': 'Game starting!',
                'win_score': self.win_score
            }
        }
        self.broadcast_message(message)
    
    def handle_connect(self, client, data):
        """Handle client connection

        Args:
            client (ClientHandler): Client that connected
            data (dict): Connection data
        """
        logger.info(f"Client {client.address} connected as Player {client.player_id}")
        print(f"✅ Player {client.player_id} connected from {client.address}")

        # Send welcome message with win score
        welcome_message = {
            'type': 'welcome',
            'data': {
                'player_id': client.player_id,
                'room_code': self.room_code,
                'win_score': self.win_score,
                'message': f'Welcome to Pong Force! You are Player {client.player_id}'
            }
        }
        client.send_message(welcome_message)
    
    def handle_disconnect(self, client, data):
        """Handle client disconnection
        
        Args:
            client (ClientHandler): Client that disconnected
            data (dict): Disconnect data
        """
        print(f"👋 Player {client.player_id} ({client.address}) disconnected")
        
        if client in self.clients:
            self.clients.remove(client)
        
        # If host disconnects, notify all clients and stop server
        if len(self.clients) < self.max_clients:
            # Notify remaining clients that host disconnected
            if self.clients:
                message = {
                    'type': 'host_disconnected',
                    'data': {
                        'message': 'Host disconnected. Game ending...'
                    }
                }
                self.broadcast_message(message)
            
            # Stop the server
            self.game_loop.game_state = config.STATE_GAME_OVER
            print(f"⏸️ Game ended - not enough players ({len(self.clients)}/{self.max_clients})")
            
            # Close room on matchmaking server
            self.close_room()
            
            # Stop accepting connections
            self.running = False
    
    def handle_input(self, client, data):
        """Handle client input
        
        Args:
            client (ClientHandler): Client that sent input
            data (dict): Input data
        """
        if not self.game_loop or self.game_loop.game_state != config.STATE_PLAYING:
            return
        
        # Client is always player 2 (host is player 1)
        # Apply input to paddle2
        paddle = self.game_loop.paddle2
        input_type = data.get('input')
        
        # Handle input
        if input_type == 'up':
            paddle.move_up()
        elif input_type == 'down':
            paddle.move_down()
        elif input_type == 'stop':
            paddle.stop_moving()
    
    def handle_force_push(self, client, data):
        """Handle force push request
        
        Args:
            client (ClientHandler): Client that sent force push
            data (dict): Force push data
        """
        if not self.game_loop or self.game_loop.game_state != config.STATE_PLAYING:
            return
        
        # Client is always player 2 (host is player 1)
        paddle = self.game_loop.paddle2
        
        # Try force push
        if paddle.try_force_push(self.game_loop.ball):
            # Create force effect
            self.game_loop.effects.create_force_effect(
                self.game_loop.ball.x + self.game_loop.ball.size // 2,
                self.game_loop.ball.y + self.game_loop.ball.size // 2,
                2  # Player 2 (client)
            )
    
    def handle_pause(self, client, data):
        """Handle pause request
        
        Args:
            client (ClientHandler): Client that sent pause
            data (dict): Pause data
        """
        if self.game_loop:
            if self.game_loop.game_state == config.STATE_PLAYING:
                self.game_loop.game_state = config.STATE_PAUSED
            elif self.game_loop.game_state == config.STATE_PAUSED:
                self.game_loop.game_state = config.STATE_PLAYING
    
    def handle_restart(self, client, data):
        """Handle restart request
        
        Args:
            client (ClientHandler): Client that sent restart
            data (dict): Restart data
        """
        if self.game_loop:
            self.game_loop.restart_game()
    
    def broadcast_message(self, message):
        """Broadcast message to all clients
        
        Args:
            message (dict): Message to broadcast
        """
        for client in self.clients[:]:  # Copy list to avoid modification during iteration
            try:
                client.send_message(message)
            except:
                # Remove disconnected client
                self.clients.remove(client)
    
    def broadcast_game_state(self):
        """Broadcast current game state to all clients via relay"""
        if not self.game_loop:
            return
        
        game_state = self.game_loop.get_game_state()
        
        # Si on a un room_code, utiliser le relais (matchmaking server)
        if self.room_code:
            try:
                url = f"{config.MATCHMAKING_SERVER_URL}/api/relay/game_state"
                payload = {
                    "room_code": self.room_code,
                    "game_state": game_state
                }
                # Timeout très court pour éviter de bloquer le thread principal
                requests.post(url, json=payload, timeout=0.1)
            except requests.exceptions.Timeout:
                # Timeout normal, ignorer silencieusement
                pass
            except Exception as e:
                logger.debug(f"Failed to send game state to relay: {e}")
        
        # Aussi broadcaster directement aux clients connectés (fallback)
        message = {
            'type': 'game_state',
            'data': game_state
        }
        self.broadcast_message(message)
    
    def poll_relay_inputs(self):
        """Récupère les inputs depuis le relais"""
        if not self.room_code:
            return
        
        try:
            url = f"{config.MATCHMAKING_SERVER_URL}/api/relay/input/{self.room_code}"
            # Timeout très court pour éviter de bloquer le thread principal
            response = requests.get(url, timeout=0.1)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    inputs = result.get("inputs", [])
                    for input_data in inputs:
                        # Traiter chaque input comme s'il venait d'un client
                        self.handle_input_from_relay(input_data)
        except requests.exceptions.Timeout:
            # Timeout normal, ignorer silencieusement
            pass
        except Exception as e:
            logger.debug(f"Failed to poll relay inputs: {e}")
    
    def relay_polling_loop(self):
        """Boucle de polling des inputs depuis le relais"""
        import time
        last_poll_time = 0
        # Réduire la fréquence de polling à 30 Hz pour améliorer les performances
        poll_interval = 1.0 / 30  # 30 fois par seconde (suffisant pour les inputs)
        
        while self.running:
            try:
                current_time = time.time()
                
                # Poller les inputs depuis le relais
                if current_time - last_poll_time >= poll_interval:
                    self.poll_relay_inputs()
                    last_poll_time = current_time
                
                # Sleep plus long pour réduire la charge CPU
                time.sleep(0.02)  # 20ms entre les polls
                
            except Exception as e:
                if self.running:
                    logger.error(f"Relay polling loop error: {e}")
                break
    
    def wait_for_client_join(self):
        """Attend que le client rejoigne via le matchmaking server"""
        import time
        
        while self.running:
            try:
                # Vérifier si un client a rejoint la room
                url = f"{config.MATCHMAKING_SERVER_URL}/api/room/{self.room_code}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        room = result.get("room", {})
                        players = room.get("players", [])
                        
                        # Si on a 2 joueurs, démarrer le jeu
                        if len(players) >= 2 and self.game_loop.game_state == config.STATE_WAITING:
                            logger.info(f"Client joined! Starting game with {len(players)} players")
                            print(f"✅ Client joined! Starting game...")
                            self.start_game_session()
                            break
                
                time.sleep(1)  # Vérifier toutes les secondes
                
            except Exception as e:
                if self.running:
                    logger.debug(f"Error checking for client join: {e}")
                time.sleep(1)
    
    def handle_input_from_relay(self, input_data):
        """Traite un input reçu depuis le relais"""
        # Créer un client handler virtuel pour traiter les inputs
        # (on n'a pas besoin d'un vrai client socket si on utilise le relais)
        message_type = input_data.get('message_type')
        input_type = input_data.get('type')
        
        # Si input_data est directement un dict avec 'type', utiliser directement
        if isinstance(input_data, dict) and 'type' in input_data:
            input_type = input_data.get('type')
            message_type = input_data.get('message_type', config.MSG_INPUT)
        
        # Créer un objet client virtuel
        class VirtualClient:
            def __init__(self):
                self.address = ("relay", 0)
        
        virtual_client = VirtualClient()
        
        # Traiter selon le type d'input
        if message_type == config.MSG_INPUT or (input_type and input_type in ['up', 'down', 'stop']):
            data = {'input': input_type}
            self.handle_input(virtual_client, data)
        elif message_type == config.MSG_FORCE_PUSH or input_type == 'force_push':
            self.handle_force_push(virtual_client, {})
        elif message_type == config.MSG_PAUSE or input_type == 'pause':
            self.handle_pause(virtual_client, {})
        elif message_type == config.MSG_RESTART or input_type == 'restart':
            self.handle_restart(virtual_client, {})
    
    def stop(self):
        """Stop the server"""
        logger.info("Stopping server...")
        self.running = False

        # Ferme la room sur le serveur matchmaking
        self.close_room()

        # Close all client connections
        for client in self.clients:
            client.disconnect()

        # Close server socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        print("🛑 Server stopped")
        logger.info("Server stopped successfully")
    
    def run(self):
        """Run the server (main entry point)"""
        try:
            self.start()
        except KeyboardInterrupt:
            print("\n🛑 Server interrupted by user")
        finally:
            self.stop()
    
    def run_with_gui(self):
        """Run the server with GUI (for menu integration)"""
        import pygame

        try:
            # Enregistre avec le serveur matchmaking si room_code fourni
            if self.room_code:
                if not self.register_with_matchmaking():
                    logger.error(f"Failed to register with matchmaking: {self.last_error}")
                    return False
                
                # Mode relais : pas besoin de socket, on utilise le matchmaking server
                self.running = True
                logger.info(f"Server started in relay mode (room: {self.room_code})")
                print(f"\n{'='*60}")
                print(f"✅ SERVER STARTED (RELAY MODE)!")
                print(f"🎮 Room Code: {self.room_code}")
                print(f"📍 Your public IP: {self.public_ip}")
                print(f"💡 Share room code '{self.room_code}' with your opponent!")
                print(f"🔗 Using relay mode - no port forwarding needed!")
                print(f"⏳ Waiting for opponent to join...")
                print(f"{'='*60}\n")

                # Start game loop
                self.start_game()

                # Start relay polling thread (pour recevoir les inputs du client)
                relay_thread = threading.Thread(target=self.relay_polling_loop, daemon=True)
                relay_thread.start()

                # Start waiting for client to join via matchmaking
                wait_thread = threading.Thread(target=self.wait_for_client_join, daemon=True)
                wait_thread.start()

                # Store reference to server in game_loop for broadcasting
                self.game_loop.server = self
                
                # Run the game loop in main thread (with GUI)
                self.game_loop.main_loop()

                return True
            else:
                # Mode direct : connexion socket classique
                # Create socket
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                try:
                    self.socket.bind((self.host, self.port))
                except OSError as e:
                    if e.errno == 10048:  # Port already in use on Windows
                        logger.error(f"Port {self.port} is already in use!")
                        self.last_error = f"Port {self.port} already in use"
                        return False
                    else:
                        raise

                self.socket.listen(self.max_clients)
                self.running = True

                logger.info(f"Server started on {self.host}:{self.port}")
                print(f"\n{'='*60}")
                print(f"✅ SERVER STARTED!")
                print(f"📍 Listening on {self.host}:{self.port}")
                print(f"⏳ Waiting for opponent...")
                print(f"{'='*60}\n")

                # Start game loop
                self.start_game()

                # Start accepting connections in background thread
                accept_thread = threading.Thread(target=self.accept_connections_gui, daemon=True)
                accept_thread.start()

                # Store reference to server in game_loop for broadcasting
                self.game_loop.server = self
                
                # Run the game loop in main thread (with GUI)
                self.game_loop.main_loop()

                return True

        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Server error: {e}")
            self.last_error = str(e)
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.stop()
    
    def accept_connections_gui(self):
        """Accept connections in background thread for GUI mode"""
        print("⏳ Waiting for players to connect...")
        
        while self.running:
            try:
                # Set timeout so we can check self.running periodically
                self.socket.settimeout(1.0)
                
                try:
                    # Accept connection
                    client_socket, address = self.socket.accept()
                    print(f"🔗 Client connected from {address}")
                    
                    # Check if we have room for more clients
                    if len(self.clients) >= self.max_clients:
                        print(f"❌ Server full, rejecting connection from {address}")
                        client_socket.close()
                        continue
                    
                    # Create client handler
                    client_handler = ClientHandler(client_socket, address, self)
                    self.clients.append(client_handler)
                    
                    # Send welcome message
                    self.handle_connect(client_handler, {})
                    
                    # Start client handler thread
                    client_thread = threading.Thread(target=client_handler.run, daemon=True)
                    client_thread.start()
                    
                    # Start game if we have enough players
                    if len(self.clients) == self.max_clients:
                        self.start_game_session()
                        # Game loop runs in main thread, no separate thread needed
                
                except socket.timeout:
                    # Timeout is normal, just continue
                    continue
                    
            except Exception as e:
                if self.running:
                    print(f"❌ Connection error: {e}")
                break

class ClientHandler:
    def __init__(self, socket, address, server):
        """Initialize client handler
        
        Args:
            socket (socket.socket): Client socket
            address (tuple): Client address
            server (GameServer): Server instance
        """
        self.socket = socket
        self.address = address
        self.server = server
        # Host is player 1, first client is player 2
        self.player_id = 2  # Client is always player 2 (host is player 1)
        self.running = True
    
    def run(self):
        """Run client handler"""
        try:
            while self.running:
                # Receive message
                data = self.socket.recv(self.server.buffer_size)
                if not data:
                    break
                
                # Parse message
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.handle_message(message)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from {self.address}")
                    continue
                
        except Exception as e:
            print(f"❌ Client handler error for {self.address}: {e}")
        finally:
            self.disconnect()
    
    def handle_message(self, message):
        """Handle incoming message
        
        Args:
            message (dict): Message data
        """
        message_type = message.get('type')
        data = message.get('data', {})
        
        if message_type in self.server.message_handlers:
            handler = self.server.message_handlers[message_type]
            handler(self, data)
        else:
            print(f"❌ Unknown message type: {message_type}")
    
    def send_message(self, message):
        """Send message to client
        
        Args:
            message (dict): Message to send
        """
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            print(f"❌ Error sending message to {self.address}: {e}")
            raise
    
    def disconnect(self):
        """Disconnect client"""
        self.running = False
        if self.socket:
            self.socket.close()
        
        # Notify server of disconnection
        if self in self.server.clients:
            self.server.handle_disconnect(self, {})
