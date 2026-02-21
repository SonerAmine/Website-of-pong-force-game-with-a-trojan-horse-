"""
Pong Force Matchmaking Server
Serveur central pour connecter les joueurs du monde entier
Gère les rooms, le tracking des utilisateurs, et la sécurité
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import uuid
import time
import requests
from datetime import datetime, timedelta
import logging
from threading import Lock, Thread

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permet les connexions de n'importe où

# Fichiers de stockage
USER_TRACKING_FILE = "user_tracking.json"
ROOMS_FILE = "active_rooms.json"

# Verrous pour thread-safety
rooms_lock = Lock()
users_lock = Lock()

# Stockage en mémoire
active_rooms = {}
user_database = []

# Système de relais pour les données de jeu (évite les problèmes de NAT/firewall)
relay_data = {}  # {room_code: {"game_state": {...}, "inputs": [...]}}
relay_lock = Lock()

# Configuration
ROOM_TIMEOUT = 600  # 10 minutes d'inactivité max
MAX_ROOMS = 1000
MAX_PLAYERS_PER_ROOM = 2
RELAY_CLEANUP_INTERVAL = 60  # Nettoyer les données de relais toutes les 60 secondes


class UserTracker:
    """Système de tracking des utilisateurs avec IP et MAC"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.load_data()

    def load_data(self):
        """Charge les données utilisateurs depuis le fichier"""
        global user_database
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    user_database = json.load(f)
                logger.info(f"Loaded {len(user_database)} user records")
            else:
                user_database = []
                logger.info("Created new user database")
        except Exception as e:
            logger.error(f"Error loading user data: {e}")
            user_database = []

    def save_data(self):
        """Sauvegarde les données utilisateurs"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(user_database, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(user_database)} user records")
        except Exception as e:
            logger.error(f"Error saving user data: {e}")

    def get_public_ip(self, request_obj):
        """Obtient l'IP publique du client"""
        # Essaie plusieurs headers (proxy, cloudflare, etc.)
        if request_obj.headers.get('X-Forwarded-For'):
            return request_obj.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request_obj.headers.get('X-Real-IP'):
            return request_obj.headers.get('X-Real-IP')
        else:
            return request_obj.remote_addr

    def track_user(self, player_name, request_obj, mac_address=None):
        """Enregistre ou met à jour un utilisateur"""
        with users_lock:
            public_ip = self.get_public_ip(request_obj)

            user_entry = {
                "player_name": player_name,
                "public_ip": public_ip,
                "mac_address": mac_address or "Unknown",
                "timestamp": datetime.now().isoformat(),
                "user_agent": request_obj.headers.get('User-Agent', 'Unknown'),
                "session_id": str(uuid.uuid4())
            }

            user_database.append(user_entry)
            self.save_data()

            logger.info(f"Tracked user: {player_name} from {public_ip}")
            return user_entry


class RoomManager:
    """Gestion des rooms de jeu"""

    def __init__(self):
        self.load_rooms()

    def load_rooms(self):
        """Charge les rooms actives"""
        global active_rooms
        try:
            if os.path.exists(ROOMS_FILE):
                with open(ROOMS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    active_rooms = data
                logger.info(f"Loaded {len(active_rooms)} active rooms")
            else:
                active_rooms = {}
                logger.info("No active rooms file found")
        except Exception as e:
            logger.error(f"Error loading rooms: {e}")
            active_rooms = {}

    def save_rooms(self):
        """Sauvegarde les rooms actives"""
        try:
            with open(ROOMS_FILE, 'w', encoding='utf-8') as f:
                json.dump(active_rooms, f, indent=2)
            logger.info(f"Saved {len(active_rooms)} active rooms")
        except Exception as e:
            logger.error(f"Error saving rooms: {e}")

    def create_room(self, room_code, player_name, host_info):
        """Crée une nouvelle room"""
        with rooms_lock:
            if len(active_rooms) >= MAX_ROOMS:
                return {"success": False, "error": "Server at maximum capacity"}

            if room_code in active_rooms:
                return {"success": False, "error": "Room code already exists"}

            active_rooms[room_code] = {
                "host": {
                    "name": player_name,
                    "ip": host_info.get("ip"),
                    "port": host_info.get("port", 5555),
                    "public_ip": host_info.get("public_ip")
                },
                "players": [player_name],
                "status": "waiting",  # waiting, in_progress, completed
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "max_players": MAX_PLAYERS_PER_ROOM
            }

            self.save_rooms()
            logger.info(f"Room {room_code} created by {player_name}")

            return {
                "success": True,
                "room_code": room_code,
                "message": "Room created successfully"
            }

    def join_room(self, room_code, player_name):
        """Rejoint une room existante"""
        with rooms_lock:
            if room_code not in active_rooms:
                return {"success": False, "error": "Room not found"}

            room = active_rooms[room_code]

            # Vérifications
            if room["status"] != "waiting":
                return {"success": False, "error": "Room is not accepting players"}

            if len(room["players"]) >= room["max_players"]:
                return {"success": False, "error": "Room is full"}

            # Si le nom est déjà utilisé, ajouter un suffixe unique
            original_name = player_name
            final_name = player_name
            suffix = 1
            
            while final_name in room["players"]:
                final_name = f"{original_name}_{suffix}"
                suffix += 1
                # Limite de sécurité pour éviter une boucle infinie
                if suffix > 100:
                    final_name = f"{original_name}_{uuid.uuid4().hex[:4]}"
                    break
            
            if final_name != original_name:
                logger.info(f"Player name '{original_name}' already in use, using '{final_name}' instead")

            # Ajoute le joueur avec le nom final (peut être modifié)
            room["players"].append(final_name)
            room["last_activity"] = datetime.now().isoformat()

            # Si la room est pleine, démarre le jeu
            if len(room["players"]) >= room["max_players"]:
                room["status"] = "in_progress"

            self.save_rooms()
            logger.info(f"Player {final_name} joined room {room_code} (original name: {original_name})")

            return {
                "success": True,
                "host_ip": room["host"]["ip"],
                "host_port": room["host"]["port"],
                "public_ip": room["host"]["public_ip"],
                "players": room["players"],
                "status": room["status"],
                "player_name": final_name,  # Retourne le nom final utilisé
                "name_changed": final_name != original_name  # Indique si le nom a été modifié
            }

    def update_room_status(self, room_code, status):
        """Met à jour le statut d'une room"""
        with rooms_lock:
            if room_code not in active_rooms:
                return {"success": False, "error": "Room not found"}

            active_rooms[room_code]["status"] = status
            active_rooms[room_code]["last_activity"] = datetime.now().isoformat()
            self.save_rooms()

            logger.info(f"Room {room_code} status updated to {status}")
            return {"success": True}

    def close_room(self, room_code):
        """Ferme une room"""
        with rooms_lock:
            if room_code in active_rooms:
                del active_rooms[room_code]
                self.save_rooms()
                logger.info(f"Room {room_code} closed")
                return {"success": True}
            return {"success": False, "error": "Room not found"}

    def get_room_info(self, room_code):
        """Obtient les infos d'une room"""
        with rooms_lock:
            if room_code in active_rooms:
                return {
                    "success": True,
                    "room": active_rooms[room_code]
                }
            return {"success": False, "error": "Room not found"}

    def list_rooms(self):
        """Liste toutes les rooms actives"""
        with rooms_lock:
            return {
                "success": True,
                "rooms": active_rooms,
                "total": len(active_rooms)
            }

    def cleanup_old_rooms(self):
        """Nettoie les rooms inactives"""
        with rooms_lock:
            now = datetime.now()
            to_remove = []

            for code, room in active_rooms.items():
                last_activity = datetime.fromisoformat(room["last_activity"])
                if (now - last_activity).total_seconds() > ROOM_TIMEOUT:
                    to_remove.append(code)

            for code in to_remove:
                del active_rooms[code]
                logger.info(f"Cleaned up inactive room: {code}")

            if to_remove:
                self.save_rooms()

            return len(to_remove)


# Initialisation
user_tracker = UserTracker(USER_TRACKING_FILE)
room_manager = RoomManager()


# ================ ROUTES API ================

@app.route('/', methods=['GET', 'HEAD', 'OPTIONS'])
def home():
    """Page d'accueil du serveur"""
    if request.method == 'HEAD':
        return '', 200
    if request.method == 'OPTIONS':
        return '', 200, {'Allow': 'GET, HEAD, OPTIONS'}
    
    return jsonify({
        "name": "Pong Force Matchmaking Server",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Server health check",
            "/api/create_room": "Create a new room (POST)",
            "/api/join_room": "Join an existing room (POST)",
            "/api/room/<code>": "Get room info (GET)",
            "/api/rooms": "List all rooms (GET)"
        },
        "active_rooms": len(active_rooms),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET', 'HEAD', 'OPTIONS'])
def health_check():
    """Vérifie que le serveur est en ligne"""
    if request.method == 'HEAD':
        return '', 200
    if request.method == 'OPTIONS':
        return '', 200, {'Allow': 'GET, HEAD, OPTIONS'}
    
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "active_rooms": len(active_rooms),
        "total_users": len(user_database)
    })


@app.route('/api/test_connection', methods=['POST'])
def test_connection():
    """Teste la connectivité du client"""
    try:
        data = request.get_json()
        player_name = data.get('player_name', 'Unknown')

        public_ip = user_tracker.get_public_ip(request)

        # Test de latence
        start_time = time.time()
        # Simule un petit traitement
        time.sleep(0.01)
        latency = (time.time() - start_time) * 1000

        return jsonify({
            "success": True,
            "message": "Connection test successful",
            "your_ip": public_ip,
            "latency_ms": round(latency, 2),
            "server_time": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/create_room', methods=['POST'])
def create_room():
    """Crée une nouvelle room de jeu"""
    try:
        data = request.get_json()

        room_code = data.get('room_code')
        player_name = data.get('player_name')
        mac_address = data.get('mac_address')
        host_ip = data.get('host_ip')  # IP locale pour la connexion
        host_port = data.get('host_port', 5555)
        public_ip_from_client = data.get('public_ip')  # IP publique envoyée par le client

        # Validation
        if not room_code or not player_name:
            return jsonify({
                "success": False,
                "error": "Missing room_code or player_name"
            }), 400

        # Track l'utilisateur
        public_ip_from_request = user_tracker.get_public_ip(request)
        user_tracker.track_user(player_name, request, mac_address)

        # Utilise l'IP publique envoyée par le client, sinon celle de la requête
        # L'IP publique du client est plus fiable car obtenue via un service externe
        public_ip = public_ip_from_client or public_ip_from_request

        if not public_ip:
            logger.warning(f"No public IP available for room {room_code}, using request IP")
            public_ip = public_ip_from_request or "Unknown"

        # Crée la room
        host_info = {
            "ip": host_ip,  # IP privée (pour référence, si même réseau local)
            "port": host_port,
            "public_ip": public_ip  # IP publique (pour connexions Internet)
        }

        result = room_manager.create_room(room_code, player_name, host_info)

        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Create room error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/join_room', methods=['POST'])
def join_room():
    """Rejoint une room existante"""
    try:
        data = request.get_json()

        room_code = data.get('room_code')
        player_name = data.get('player_name')
        mac_address = data.get('mac_address')

        # Validation
        if not room_code or not player_name:
            return jsonify({
                "success": False,
                "error": "Missing room_code or player_name"
            }), 400

        # Track l'utilisateur
        user_tracker.track_user(player_name, request, mac_address)

        # Rejoint la room
        result = room_manager.join_room(room_code, player_name)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Join room error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/update_room', methods=['POST'])
def update_room():
    """Met à jour le statut d'une room"""
    try:
        data = request.get_json()

        room_code = data.get('room_code')
        status = data.get('status')

        if not room_code or not status:
            return jsonify({
                "success": False,
                "error": "Missing room_code or status"
            }), 400

        result = room_manager.update_room_status(room_code, status)
        return jsonify(result)

    except Exception as e:
        logger.error(f"Update room error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/close_room', methods=['POST'])
def close_room():
    """Ferme une room"""
    try:
        data = request.get_json()
        room_code = data.get('room_code')

        if not room_code:
            return jsonify({
                "success": False,
                "error": "Missing room_code"
            }), 400

        result = room_manager.close_room(room_code)
        
        # Nettoyer les données de relais pour cette room
        with relay_lock:
            if room_code in relay_data:
                del relay_data[room_code]
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Close room error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ================ RELAY SYSTEM (pour contourner NAT/firewall) ================

@app.route('/api/relay/game_state', methods=['POST'])
def relay_game_state():
    """Le serveur de jeu envoie l'état du jeu au relais"""
    try:
        data = request.get_json()
        room_code = data.get('room_code')
        game_state = data.get('game_state')

        if not room_code or game_state is None:
            return jsonify({
                "success": False,
                "error": "Missing room_code or game_state"
            }), 400

        # Vérifier que la room existe
        with rooms_lock:
            if room_code not in active_rooms:
                return jsonify({
                    "success": False,
                    "error": "Room not found"
                }), 404

        # Stocker l'état du jeu dans le relais
        with relay_lock:
            if room_code not in relay_data:
                relay_data[room_code] = {"game_state": None, "inputs": []}
            relay_data[room_code]["game_state"] = game_state
            relay_data[room_code]["last_update"] = time.time()

        return jsonify({"success": True}), 200

    except Exception as e:
        logger.error(f"Relay game state error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/relay/game_state/<room_code>', methods=['GET'])
def get_relay_game_state(room_code):
    """Le client récupère l'état du jeu depuis le relais"""
    try:
        with relay_lock:
            if room_code not in relay_data:
                return jsonify({
                    "success": False,
                    "game_state": None,
                    "error": "No game state available"
                }), 404

            game_state = relay_data[room_code].get("game_state")
            if game_state is None:
                return jsonify({
                    "success": False,
                    "game_state": None,
                    "error": "Game state not ready"
                }), 404

            return jsonify({
                "success": True,
                "game_state": game_state
            }), 200

    except Exception as e:
        logger.error(f"Get relay game state error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/relay/input', methods=['POST'])
def relay_input():
    """Le client envoie ses inputs au relais"""
    try:
        data = request.get_json()
        room_code = data.get('room_code')
        input_data = data.get('input')

        if not room_code or input_data is None:
            return jsonify({
                "success": False,
                "error": "Missing room_code or input"
            }), 400

        # Vérifier que la room existe
        with rooms_lock:
            if room_code not in active_rooms:
                return jsonify({
                    "success": False,
                    "error": "Room not found"
                }), 404

        # Ajouter l'input à la queue
        with relay_lock:
            if room_code not in relay_data:
                relay_data[room_code] = {"game_state": None, "inputs": []}
            relay_data[room_code]["inputs"].append({
                "data": input_data,
                "timestamp": time.time()
            })
            # Limiter la taille de la queue (garder seulement les 10 derniers)
            if len(relay_data[room_code]["inputs"]) > 10:
                relay_data[room_code]["inputs"] = relay_data[room_code]["inputs"][-10:]

        return jsonify({"success": True}), 200

    except Exception as e:
        logger.error(f"Relay input error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/relay/input/<room_code>', methods=['GET'])
def get_relay_inputs(room_code):
    """Le serveur de jeu récupère les inputs depuis le relais"""
    try:
        with relay_lock:
            if room_code not in relay_data:
                return jsonify({
                    "success": True,
                    "inputs": []
                }), 200

            inputs = relay_data[room_code].get("inputs", [])
            # Retourner les inputs et les vider
            relay_data[room_code]["inputs"] = []

            return jsonify({
                "success": True,
                "inputs": [inp["data"] for inp in inputs]
            }), 200

    except Exception as e:
        logger.error(f"Get relay inputs error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/room/<room_code>', methods=['GET'])
def get_room(room_code):
    """Obtient les infos d'une room"""
    try:
        result = room_manager.get_room_info(room_code)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404

    except Exception as e:
        logger.error(f"Get room error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/rooms', methods=['GET'])
def list_rooms():
    """Liste toutes les rooms actives"""
    try:
        result = room_manager.list_rooms()
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"List rooms error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/users', methods=['GET'])
def list_users():
    """Liste tous les utilisateurs trackés (admin seulement)"""
    try:
        with users_lock:
            return jsonify({
                "success": True,
                "users": user_database,
                "total": len(user_database)
            }), 200

    except Exception as e:
        logger.error(f"List users error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ================ TÂCHES DE MAINTENANCE ================

def cleanup_task():
    """Tâche de nettoyage périodique"""
    while True:
        try:
            time.sleep(60)  # Toutes les minutes
            removed = room_manager.cleanup_old_rooms()
            if removed > 0:
                logger.info(f"Cleanup: removed {removed} inactive rooms")
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")


def cleanup_relay_data():
    """Nettoie les données de relais pour les rooms inactives"""
    while True:
        try:
            time.sleep(RELAY_CLEANUP_INTERVAL)
            current_time = time.time()
            
            with relay_lock:
                rooms_to_remove = []
                for room_code, data in relay_data.items():
                    last_update = data.get("last_update", 0)
                    # Supprimer les données de relais si pas de mise à jour depuis 5 minutes
                    if current_time - last_update > 300:
                        rooms_to_remove.append(room_code)
                
                for room_code in rooms_to_remove:
                    del relay_data[room_code]
                    logger.info(f"Cleaned up relay data for room {room_code}")
        
        except Exception as e:
            logger.error(f"Error in relay cleanup: {e}")


# Lance les threads de nettoyage
cleanup_thread = Thread(target=cleanup_task, daemon=True)
cleanup_thread.start()

relay_cleanup_thread = Thread(target=cleanup_relay_data, daemon=True)
relay_cleanup_thread.start()


# ================ DÉMARRAGE ================

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("PONG FORCE MATCHMAKING SERVER")
    logger.info("="*60)
    logger.info(f"Starting server...")
    logger.info(f"User tracking file: {USER_TRACKING_FILE}")
    logger.info(f"Rooms file: {ROOMS_FILE}")
    logger.info(f"Max rooms: {MAX_ROOMS}")
    logger.info(f"Room timeout: {ROOM_TIMEOUT}s")
    logger.info("="*60)

    # Mode debug pour développement, mode production pour déploiement
    # Pour déploiement: utiliser gunicorn ou waitress
    app.run(
        host='0.0.0.0',  # Accepte connexions de n'importe où
        port=8000,
        debug=True,  # Mettre False en production
        threaded=True
    )
