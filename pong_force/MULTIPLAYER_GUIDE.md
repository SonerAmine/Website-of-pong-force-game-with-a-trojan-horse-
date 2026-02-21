# 🎮 PONG FORCE - MULTIPLAYER GUIDE

Ce guide explique comment utiliser le système multiplayer professionnel de Pong Force pour jouer en ligne avec des joueurs du monde entier.

---

## 📋 TABLE DES MATIÈRES

1. [Installation](#installation)
2. [Démarrage du Serveur Matchmaking](#démarrage-du-serveur-matchmaking)
3. [Jouer en Multiplayer](#jouer-en-multiplayer)
4. [Tests et Diagnostic](#tests-et-diagnostic)
5. [Résolution des Problèmes](#résolution-des-problèmes)
6. [Données Utilisateurs](#données-utilisateurs)

---

## 🔧 INSTALLATION

### 1. Installer les dépendances

```bash
cd pong_force
pip install -r requirements.txt
```

### Dépendances installées:
- `pygame` - Moteur de jeu
- `Flask` - Serveur web pour matchmaking
- `Flask-CORS` - Support CORS pour connexions cross-origin
- `requests` - Client HTTP pour API calls
- `pyinstaller` - Pour créer l'exécutable

---

## 🚀 DÉMARRAGE DU SERVEUR MATCHMAKING

Le serveur matchmaking est **OBLIGATOIRE** pour jouer en ligne. Il gère les rooms et connecte les joueurs.

### Étape 1: Lancer le serveur matchmaking

```bash
cd pong_force
python matchmaking_server.py
```

### Vous verrez:
```
============================================================
PONG FORCE MATCHMAKING SERVER
============================================================
Starting server...
User tracking file: user_tracking.json
Rooms file: active_rooms.json
Max rooms: 1000
Room timeout: 600s
============================================================
 * Running on http://0.0.0.0:8000
```

### Étape 2: Vérifier que le serveur fonctionne

Ouvrez votre navigateur et allez à:
```
http://localhost:8000/health
```

Vous devriez voir:
```json
{
  "status": "online",
  "timestamp": "2024-01-01T12:00:00",
  "active_rooms": 0,
  "total_users": 0
}
```

✅ **Le serveur matchmaking est maintenant en ligne!**

---

## 🎯 JOUER EN MULTIPLAYER

### OPTION A: Héberger une Room (Host)

1. **Lancez le jeu:**
   ```bash
   python main.py
   ```

2. **Dans le menu principal:**
   - Sélectionnez `4. Multiplayer Room`

3. **Créer une room:**
   - Cliquez sur `HOST ROOM`
   - Entrez votre nom de joueur
   - Un code de room à 6 caractères sera généré (ex: `ABC123`)

4. **Attendez qu'un joueur rejoigne:**
   - Le jeu affichera: "Waiting for opponent..."
   - **Partagez le code de room avec votre ami**

5. **Le jeu démarre automatiquement** quand le 2ème joueur se connecte!

### OPTION B: Rejoindre une Room (Join)

1. **Lancez le jeu:**
   ```bash
   python main.py
   ```

2. **Dans le menu principal:**
   - Sélectionnez `4. Multiplayer Room`

3. **Rejoindre une room:**
   - Cliquez sur `JOIN ROOM`
   - Entrez le **code de room** que votre ami vous a donné (ex: `ABC123`)
   - Entrez votre nom de joueur
   - Cliquez sur `CONNECT`

4. **Connexion en cours:**
   - Le jeu teste votre connexion Internet
   - Le jeu cherche la room sur le serveur matchmaking
   - Le jeu se connecte à l'hôte

5. **Le jeu démarre!** 🎮

---

## 🧪 TESTS ET DIAGNOSTIC

### Test Complet du Système

Pour tester tout le système (menu, multiplayer, réseau):

```bash
python test_gameplay.py
```

### Tests Réseau Manuels

#### 1. Test de Connexion Internet
```python
from network.network_utils import NetworkUtils

# Test de base
result = NetworkUtils.test_internet_connection()
print(result)  # {'connected': True, 'latency_ms': 45.2}

# Obtenir votre IP publique
public_ip = NetworkUtils.get_public_ip()
print(f"Votre IP publique: {public_ip}")

# Obtenir votre adresse MAC
mac = NetworkUtils.get_mac_address()
print(f"Votre MAC: {mac}")
```

#### 2. Test du Serveur Matchmaking
```python
from network.network_utils import NetworkUtils
import config

result = NetworkUtils.test_matchmaking_server(config.MATCHMAKING_SERVER_URL)
print(result)
# {'online': True, 'latency_ms': 12.5, 'info': {...}}
```

#### 3. Diagnostic Complet
```python
from network.network_utils import ConnectionTester
import config

tester = ConnectionTester(config.MATCHMAKING_SERVER_URL)
results = tester.run_full_test()

print(tester.get_summary())
```

Cela affichera:
```
=== CONNECTION TEST SUMMARY ===
Status: PASSED
Can play multiplayer: True

Local Network:
  IP: 192.168.1.100
  MAC: AA:BB:CC:DD:EE:FF

Internet:
  Connected: True
  Latency: 45ms

Matchmaking Server:
  Online: True
  Latency: 12ms
==============================
```

---

## 🔧 RÉSOLUTION DES PROBLÈMES

### Problème 1: "Cannot reach matchmaking server"

**Cause:** Le serveur matchmaking n'est pas démarré.

**Solution:**
```bash
# Terminal 1: Démarrer le serveur matchmaking
python matchmaking_server.py

# Terminal 2: Lancer le jeu
python main.py
```

### Problème 2: "Connection test failed"

**Cause:** Pas de connexion Internet ou firewall bloque la connexion.

**Solution:**
1. Vérifiez votre connexion Internet
2. Désactivez temporairement le firewall/antivirus
3. Vérifiez que le port 5555 est ouvert

### Problème 3: "Room not found"

**Cause:** Le code de room est incorrect ou expiré.

**Solution:**
1. Vérifiez que le code est correct (6 caractères)
2. L'hôte doit créer la room **avant** que vous ne la rejoigniez
3. Les rooms expirent après 10 minutes d'inactivité

### Problème 4: "Port already in use"

**Cause:** Une autre instance du jeu utilise le port 5555.

**Solution:**
```bash
# Windows: Tuer le processus sur le port 5555
netstat -ano | findstr :5555
taskkill /PID <PID> /F

# Ou redémarrer votre ordinateur
```

### Problème 5: High Latency / Lag

**Cause:** Connexion Internet lente ou distance géographique.

**Solution:**
1. Fermez les autres applications utilisant Internet
2. Utilisez une connexion câblée (Ethernet) plutôt que WiFi
3. Jouez avec des personnes proches géographiquement

### Problème 6: "Cannot obtain public IP"

**Cause:** Services d'IP publique bloqués ou firewall.

**Solution:**
1. Vérifiez votre connexion Internet
2. Testez manuellement: Allez sur `https://api.ipify.org` dans votre navigateur
3. Configurez votre firewall pour autoriser les connexions sortantes

---

## 📊 DONNÉES UTILISATEURS

### Fichier: `user_tracking.json`

Ce fichier stocke les informations de **tous les utilisateurs** qui se connectent au multiplayer:

```json
[
  {
    "player_name": "Player1",
    "public_ip": "203.0.113.45",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "timestamp": "2024-01-01T12:00:00",
    "user_agent": "Python/3.11",
    "session_id": "uuid-here"
  },
  {
    "player_name": "Player2",
    "public_ip": "198.51.100.23",
    "mac_address": "11:22:33:44:55:66",
    "timestamp": "2024-01-01T12:05:00",
    "user_agent": "Python/3.11",
    "session_id": "uuid-here"
  }
]
```

### Informations Stockées:

- **player_name**: Nom du joueur
- **public_ip**: Adresse IP publique (visible sur Internet)
- **mac_address**: Adresse MAC de la carte réseau
- **timestamp**: Date/heure de connexion
- **user_agent**: Information sur le client
- **session_id**: Identifiant unique de session

### Fichier: `active_rooms.json`

Ce fichier stocke les **rooms actives**:

```json
{
  "ABC123": {
    "host": {
      "name": "Player1",
      "ip": "192.168.1.100",
      "port": 5555,
      "public_ip": "203.0.113.45"
    },
    "players": ["Player1", "Player2"],
    "status": "in_progress",
    "created_at": "2024-01-01T12:00:00",
    "last_activity": "2024-01-01T12:05:00",
    "max_players": 2
  }
}
```

### API Endpoints du Serveur Matchmaking:

- `GET /health` - Vérifier le statut du serveur
- `POST /api/test_connection` - Tester la connexion
- `POST /api/create_room` - Créer une room
- `POST /api/join_room` - Rejoindre une room
- `POST /api/update_room` - Mettre à jour le statut
- `POST /api/close_room` - Fermer une room
- `GET /api/room/<code>` - Obtenir info d'une room
- `GET /api/rooms` - Lister toutes les rooms
- `GET /api/users` - Lister tous les utilisateurs (admin)

### Exemple d'utilisation de l'API:

```python
import requests

# Créer une room
response = requests.post('http://localhost:8000/api/create_room', json={
    "room_code": "ABC123",
    "player_name": "Player1",
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "host_ip": "192.168.1.100",
    "host_port": 5555
})

print(response.json())
# {'success': True, 'room_code': 'ABC123', 'message': 'Room created successfully'}
```

---

## 🌐 DÉPLOIEMENT EN PRODUCTION

Pour permettre à des joueurs du **monde entier** de jouer ensemble:

### Option 1: Heroku (Gratuit)

1. Créez un compte sur heroku.com
2. Installez Heroku CLI
3. Déployez le serveur matchmaking:

```bash
# Dans le dossier pong_force/
heroku create pong-force-matchmaking
git add matchmaking_server.py requirements.txt
git commit -m "Deploy matchmaking"
git push heroku main
```

4. Mettez à jour `config.py`:
```python
MATCHMAKING_SERVER_URL = "https://pong-force-matchmaking.herokuapp.com"
```

### Option 2: VPS Personnel

1. Louez un VPS (DigitalOcean, AWS, etc.)
2. Installez Python et les dépendances
3. Lancez le serveur:

```bash
# Sur le VPS
python matchmaking_server.py

# Ou utilisez gunicorn pour la production
gunicorn -w 4 -b 0.0.0.0:8000 matchmaking_server:app
```

4. Configurez un nom de domaine
5. Mettez à jour `config.py` avec votre URL

---

## 🎮 CONTRÔLES DU JEU

### Joueur Hôte (Player 1):
- **↑/↓** ou **W/S**: Déplacer la raquette
- **ESPACE** ou **SHIFT**: Force Push (quand la jauge est pleine)

### Joueur Invité (Player 2):
- **↑/↓** ou **W/S**: Déplacer la raquette
- **ESPACE** ou **SHIFT**: Force Push (quand la jauge est pleine)

### Général:
- **ESC**: Pause
- **R**: Restart (après game over)

---

## 📝 NOTES IMPORTANTES

1. **Le serveur matchmaking DOIT être en ligne** pour jouer en multiplayer
2. **Les deux joueurs doivent avoir une connexion Internet**
3. **Le port 5555 doit être ouvert** sur l'ordinateur de l'hôte
4. **Les rooms expirent après 10 minutes** d'inactivité
5. **Maximum 1000 rooms actives** simultanément sur le serveur
6. **Les données utilisateurs sont stockées** dans `user_tracking.json`

---

## 🆘 SUPPORT

En cas de problème:

1. Vérifiez ce guide
2. Lancez `python test_gameplay.py` pour diagnostiquer
3. Vérifiez les logs du serveur matchmaking
4. Vérifiez votre firewall/antivirus

---

## 🎉 AMUSEZ-VOUS BIEN!

Le système multiplayer est maintenant complètement opérationnel. Partagez des codes de room avec vos amis et profitez de Pong Force en ligne!

**Bon jeu! 🏓⚡**
