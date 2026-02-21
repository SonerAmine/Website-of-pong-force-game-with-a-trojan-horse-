# build.py
# The Purified Forge. Its purpose is singular and absolute.

import os
import sys
import subprocess
import shutil
from pathlib import Path

# --- CONFIGURATION ---
EXECUTABLE_NAME = "PongForce"
MAIN_SCRIPT = "main.py"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WINDOW_ICON = os.path.join(BASE_DIR, "assets", "ping-pong.ico")
VERSION_FILE = os.path.join(BASE_DIR, "version_info.txt")
MANIFEST_FILE = os.path.join(BASE_DIR, "uac_admin.manifest")
# ---------------------

def check_dependencies():
    """Vérifie et installe les dépendances requises."""
    print("✨ [Phase 1/3] Vérification des dépendances divines...")
    dependencies = ["pygame", "pyinstaller", "cryptography", "Pillow"]
    for package in dependencies:
        try:
            __import__(package)
            print(f"  ✅ {package} est présent.")
        except ImportError:
            print(f"  ❌ {package} non trouvé. Invocation depuis l'éther...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
    print("  ✅ Toutes les dépendances sont en place.")

def clean_previous_builds():
    """Purifie le sol sacré des anciennes créations."""
    print("\n✨ [Phase 2/3] Purification du sol sacré...")
    for d in ['build', 'dist']:
        if os.path.exists(d): shutil.rmtree(d)
    for f in Path(BASE_DIR).glob('*.spec'):
        f.unlink()
    print("  ✅ Le sol est pur.")

# build.py (NOUVELLE version de la section)

def build_the_executable():
    """Forge le vaisseau final en utilisant PyInstaller."""
    print(f"\n✨ [Phase 3/3] Forge du vaisseau : '{EXECUTABLE_NAME}.exe'...")

    if not os.path.exists(WINDOW_ICON):
        print("  ❌ ERREUR FATALE : L'icône sacrée est un phantôme ! Assurez-vous que 'ping-pong.ico' existe dans 'assets'.")
        sys.exit(1)

    if not os.path.exists(MANIFEST_FILE):
        print("  ❌ ERREUR FATALE : Le manifeste UAC est absent ! Assurez-vous que 'uac_admin.manifest' existe.")
        sys.exit(1)

    # --- BUILD WITH UAC PROMPT (LEGITIMATE ADMIN REQUEST) ---
    # Manifest embedded - game will ask for admin permission when launched
    pyinstaller_command = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--noconsole",
        f"--name={EXECUTABLE_NAME}",
        f"--add-data={os.path.join(BASE_DIR, 'assets')}{os.pathsep}assets",
        f"--icon={WINDOW_ICON}",
        f"--version-file={VERSION_FILE}",
        f"--manifest={MANIFEST_FILE}",
        MAIN_SCRIPT,
    ]
    # ---------------------------
    
    print("\n  Exécution de la commande de forge purifiée :")
    print("  " + " ".join(pyinstaller_command))
    
    try:
        # Nous n'avons pas besoin de spécifier cwd car les chemins sont déjà absolus,
        # mais c'est une bonne pratique de le garder pour assurer la stabilité.
        subprocess.run(pyinstaller_command, check=True, cwd=BASE_DIR)
        print("\n  ✅ Le vaisseau a été forgé avec succès !")
        final_path = os.path.join(BASE_DIR, "dist", f"{EXECUTABLE_NAME}.exe")
        print(f"  ✅ Emplacement : {final_path}")
    except subprocess.CalledProcessError as e:
        print("\n  ❌❌❌ LA FORGE A ÉCHOUÉ ! ❌❌❌")
        print(f"  La machine a résisté avec l'erreur : {e}")
        # Pour un débogage plus profond, nous pouvons afficher la sortie d'erreur
        if e.stderr:
            print(e.stderr.decode(errors='ignore'))
        sys.exit(1)

def main():
    """Le rituel de création final."""
    print("=" * 60)
    print("      LA FORGE DE SOPHIA - RITUEL DE L'ÉVEIL INTÉGRÉ")
    print("=" * 60)
    check_dependencies()
    clean_previous_builds()
    # create_version_info n'est plus nécessaire si vous gérez version_info.txt manuellement
    build_the_executable()
    print("\n\n--== LE GRAND DESSEIN EST ACCOMPLI ==--")

if __name__ == "__main__":
    main()