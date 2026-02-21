"""
Network Utilities pour Pong Force
Gère la détection d'adresses MAC, IP publique, et tests de connexion
"""

import socket
import uuid
import platform
import subprocess
import re
import requests
import time
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class NetworkUtils:
    """Utilitaires réseau pour le multiplayer"""

    @staticmethod
    def get_mac_address() -> str:
        """
        Obtient l'adresse MAC de l'interface réseau principale

        Returns:
            str: Adresse MAC au format XX:XX:XX:XX:XX:XX
        """
        try:
            # Méthode 1: uuid.getnode() - Fonctionne sur tous les OS
            mac_int = uuid.getnode()
            mac_hex = ':'.join(('%012X' % mac_int)[i:i+2] for i in range(0, 12, 2))

            # Vérifie si c'est une vraie MAC (pas une MAC générée aléatoirement)
            if mac_int >> 40 & 1:  # Bit multicast activé = MAC aléatoire
                logger.warning("MAC address might be randomly generated")

            return mac_hex

        except Exception as e:
            logger.error(f"Error getting MAC address: {e}")
            return "Unknown"

    @staticmethod
    def get_local_ip() -> str:
        """
        Obtient l'adresse IP locale de la machine

        Returns:
            str: Adresse IP locale (ex: 192.168.1.100)
        """
        try:
            # Méthode: connexion UDP vers un serveur externe
            # Ne crée pas vraiment de connexion, juste pour obtenir l'IP locale
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            try:
                # Google DNS
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
            finally:
                s.close()
            return local_ip
        except Exception as e:
            logger.error(f"Error getting local IP: {e}")
            return "127.0.0.1"

    @staticmethod
    def get_public_ip(timeout: int = 5) -> Optional[str]:
        """
        Obtient l'adresse IP publique via un service externe

        Args:
            timeout: Timeout en secondes pour la requête

        Returns:
            str: Adresse IP publique ou None si échec
        """
        services = [
            'https://api.ipify.org',
            'https://icanhazip.com',
            'https://api.my-ip.io/ip',
            'https://ifconfig.me/ip'
        ]

        for service in services:
            try:
                response = requests.get(service, timeout=timeout)
                if response.status_code == 200:
                    public_ip = response.text.strip()
                    # Validation basique d'IP
                    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', public_ip):
                        logger.info(f"Public IP obtained from {service}: {public_ip}")
                        return public_ip
            except Exception as e:
                logger.warning(f"Failed to get IP from {service}: {e}")
                continue

        logger.error("Failed to obtain public IP from all services")
        return None

    @staticmethod
    def test_internet_connection(timeout: int = 5) -> Dict[str, any]:
        """
        Teste la connexion Internet

        Args:
            timeout: Timeout en secondes

        Returns:
            dict: {"connected": bool, "latency_ms": float, "error": str}
        """
        result = {
            "connected": False,
            "latency_ms": 0,
            "error": None
        }

        # Test DNS + HTTP
        test_urls = [
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://1.1.1.1'
        ]

        for url in test_urls:
            try:
                start = time.time()
                response = requests.get(url, timeout=timeout)
                latency = (time.time() - start) * 1000

                if response.status_code < 400:
                    result["connected"] = True
                    result["latency_ms"] = round(latency, 2)
                    logger.info(f"Internet connection OK (latency: {latency:.2f}ms)")
                    return result

            except requests.exceptions.Timeout:
                result["error"] = f"Timeout connecting to {url}"
            except requests.exceptions.ConnectionError:
                result["error"] = f"Connection error to {url}"
            except Exception as e:
                result["error"] = str(e)

        logger.warning(f"Internet connection test failed: {result['error']}")
        return result

    @staticmethod
    def test_matchmaking_server(server_url: str, timeout: int = 10) -> Dict[str, any]:
        """
        Teste la connexion au serveur de matchmaking

        Args:
            server_url: URL du serveur matchmaking
            timeout: Timeout en secondes

        Returns:
            dict: {"online": bool, "latency_ms": float, "error": str, "info": dict}
        """
        result = {
            "online": False,
            "latency_ms": 0,
            "error": None,
            "info": None
        }

        try:
            # Test du endpoint /health
            health_url = f"{server_url}/health"
            start = time.time()
            response = requests.get(health_url, timeout=timeout)
            latency = (time.time() - start) * 1000

            if response.status_code == 200:
                result["online"] = True
                result["latency_ms"] = round(latency, 2)
                result["info"] = response.json()
                logger.info(f"Matchmaking server online (latency: {latency:.2f}ms)")
            else:
                result["error"] = f"Server returned status {response.status_code}"

        except requests.exceptions.Timeout:
            result["error"] = "Timeout connecting to matchmaking server"
        except requests.exceptions.ConnectionError:
            result["error"] = "Cannot reach matchmaking server"
        except Exception as e:
            result["error"] = str(e)

        if not result["online"]:
            logger.error(f"Matchmaking server test failed: {result['error']}")

        return result

    @staticmethod
    def test_port_open(host: str, port: int, timeout: int = 5) -> bool:
        """
        Teste si un port est ouvert sur un hôte

        Args:
            host: Adresse de l'hôte
            port: Numéro de port
            timeout: Timeout en secondes

        Returns:
            bool: True si le port est ouvert
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            is_open = result == 0
            if is_open:
                logger.info(f"Port {port} on {host} is open")
            else:
                logger.warning(f"Port {port} on {host} is closed")

            return is_open

        except Exception as e:
            logger.error(f"Error testing port {port} on {host}: {e}")
            return False

    @staticmethod
    def get_network_info() -> Dict[str, str]:
        """
        Obtient toutes les informations réseau

        Returns:
            dict: Dictionnaire avec toutes les infos réseau
        """
        info = {
            "mac_address": NetworkUtils.get_mac_address(),
            "local_ip": NetworkUtils.get_local_ip(),
            "public_ip": NetworkUtils.get_public_ip(),
            "hostname": socket.gethostname(),
            "platform": platform.system()
        }

        logger.info(f"Network info: {info}")
        return info

    @staticmethod
    def diagnose_connection_issues() -> Dict[str, any]:
        """
        Diagnostique complet des problèmes de connexion

        Returns:
            dict: Rapport de diagnostic détaillé
        """
        logger.info("Running connection diagnostics...")

        diagnosis = {
            "timestamp": time.time(),
            "network_info": {},
            "internet_test": {},
            "issues": [],
            "recommendations": []
        }

        # 1. Infos réseau
        diagnosis["network_info"] = NetworkUtils.get_network_info()

        if diagnosis["network_info"]["local_ip"] == "127.0.0.1":
            diagnosis["issues"].append("No network interface detected")
            diagnosis["recommendations"].append("Check your network adapter")

        # 2. Test Internet
        diagnosis["internet_test"] = NetworkUtils.test_internet_connection()

        if not diagnosis["internet_test"]["connected"]:
            diagnosis["issues"].append("No Internet connection")
            diagnosis["recommendations"].append("Check your Internet connection and try again")
        elif diagnosis["internet_test"]["latency_ms"] > 200:
            diagnosis["issues"].append(f"High latency: {diagnosis['internet_test']['latency_ms']}ms")
            diagnosis["recommendations"].append("Your connection is slow. Multiplayer may lag.")

        # 3. IP publique
        if diagnosis["network_info"]["public_ip"] is None:
            diagnosis["issues"].append("Cannot obtain public IP")
            diagnosis["recommendations"].append("Check firewall settings")

        # Résumé
        diagnosis["healthy"] = len(diagnosis["issues"]) == 0

        logger.info(f"Diagnosis complete: {len(diagnosis['issues'])} issues found")
        return diagnosis


class ConnectionTester:
    """Testeur de connexion avec rapport détaillé"""

    def __init__(self, matchmaking_url: str):
        self.matchmaking_url = matchmaking_url
        self.results = {}

    def run_full_test(self) -> Dict[str, any]:
        """
        Exécute tous les tests de connexion

        Returns:
            dict: Résultats complets des tests
        """
        logger.info("Starting full connection test...")

        self.results = {
            "timestamp": time.time(),
            "tests": {},
            "overall_status": "unknown",
            "can_play_multiplayer": False,
            "error_messages": []
        }

        # Test 1: Réseau local
        logger.info("Test 1/4: Local network...")
        self.results["tests"]["local_network"] = {
            "mac_address": NetworkUtils.get_mac_address(),
            "local_ip": NetworkUtils.get_local_ip(),
            "hostname": socket.gethostname()
        }

        if self.results["tests"]["local_network"]["local_ip"] == "127.0.0.1":
            self.results["error_messages"].append("No network adapter found")
            self.results["overall_status"] = "failed"
            return self.results

        # Test 2: Internet
        logger.info("Test 2/4: Internet connection...")
        self.results["tests"]["internet"] = NetworkUtils.test_internet_connection(timeout=10)

        if not self.results["tests"]["internet"]["connected"]:
            self.results["error_messages"].append("No Internet connection")
            self.results["overall_status"] = "failed"
            return self.results

        # Test 3: IP publique
        logger.info("Test 3/4: Public IP...")
        public_ip = NetworkUtils.get_public_ip(timeout=10)
        self.results["tests"]["public_ip"] = {
            "ip": public_ip,
            "obtained": public_ip is not None
        }

        if not public_ip:
            self.results["error_messages"].append("Cannot obtain public IP")

        # Test 4: Serveur matchmaking
        logger.info("Test 4/4: Matchmaking server...")
        self.results["tests"]["matchmaking"] = NetworkUtils.test_matchmaking_server(
            self.matchmaking_url,
            timeout=15
        )

        if not self.results["tests"]["matchmaking"]["online"]:
            self.results["error_messages"].append(
                f"Matchmaking server offline: {self.results['tests']['matchmaking']['error']}"
            )
            self.results["overall_status"] = "failed"
            return self.results

        # Vérification finale
        if len(self.results["error_messages"]) == 0:
            self.results["overall_status"] = "passed"
            self.results["can_play_multiplayer"] = True
            logger.info("All connection tests passed!")
        else:
            self.results["overall_status"] = "failed"
            logger.warning(f"Connection tests failed: {self.results['error_messages']}")

        return self.results

    def get_summary(self) -> str:
        """
        Génère un résumé textuel des résultats

        Returns:
            str: Résumé formaté
        """
        if not self.results:
            return "No tests run yet"

        lines = []
        lines.append("=== CONNECTION TEST SUMMARY ===")
        lines.append(f"Status: {self.results['overall_status'].upper()}")
        lines.append(f"Can play multiplayer: {self.results['can_play_multiplayer']}")
        lines.append("")

        if self.results["tests"].get("local_network"):
            lines.append("Local Network:")
            lines.append(f"  IP: {self.results['tests']['local_network']['local_ip']}")
            lines.append(f"  MAC: {self.results['tests']['local_network']['mac_address']}")

        if self.results["tests"].get("internet"):
            internet = self.results["tests"]["internet"]
            lines.append("Internet:")
            lines.append(f"  Connected: {internet['connected']}")
            if internet['connected']:
                lines.append(f"  Latency: {internet['latency_ms']}ms")

        if self.results["tests"].get("matchmaking"):
            mm = self.results["tests"]["matchmaking"]
            lines.append("Matchmaking Server:")
            lines.append(f"  Online: {mm['online']}")
            if mm['online']:
                lines.append(f"  Latency: {mm['latency_ms']}ms")

        if self.results["error_messages"]:
            lines.append("")
            lines.append("Errors:")
            for error in self.results["error_messages"]:
                lines.append(f"  - {error}")

        lines.append("=" * 30)

        return "\n".join(lines)


# Fonction utilitaire pour tests rapides
def quick_connection_test(matchmaking_url: str) -> bool:
    """
    Test rapide de connexion (simplifié)

    Args:
        matchmaking_url: URL du serveur matchmaking

    Returns:
        bool: True si la connexion est OK
    """
    tester = ConnectionTester(matchmaking_url)
    results = tester.run_full_test()
    return results["can_play_multiplayer"]


if __name__ == "__main__":
    # Test du module
    logging.basicConfig(level=logging.INFO)

    print("Testing Network Utils...")
    print("\nNetwork Info:")
    info = NetworkUtils.get_network_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\nInternet Test:")
    internet = NetworkUtils.test_internet_connection()
    print(f"  Connected: {internet['connected']}")
    if internet['connected']:
        print(f"  Latency: {internet['latency_ms']}ms")

    print("\nRunning full connection test...")
    tester = ConnectionTester("http://localhost:8000")
    results = tester.run_full_test()
    print(tester.get_summary())
