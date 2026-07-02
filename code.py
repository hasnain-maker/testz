import socket
import os
import time
import threading
from datetime import datetime

LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 9998
SAVE_FOLDER = "received_folders"
BUFFER_SIZE = 8192

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

print("="*60)
print("📥 KALI RECEIVER - ULTIMATE")
print("="*60)
print(f"🎯 Listening: {LISTEN_IP}:{LISTEN_PORT}")
print(f"📁 Saving to: {SAVE_FOLDER}")
print("="*60)

# ============= SERVER WITH AUTO-RESTART =============
def create_server():
    while True:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            server.bind((LISTEN_IP, LISTEN_PORT))
            server.listen(10)  # 10 connections backlog
            print("[*] ✅ Server started successfully!")
            return server
        except Exception as e:
            print(f"[-] Error: {e}")
            print("[*] Retrying in 5 seconds...")
            time.sleep(5)

server = create_server()
print("[*] Waiting for connections...\n")

# ============= CLIENT HANDLER =============
def handle_client(client, addr):
    try:
        print(f"\n[+] Connection from: {addr}")
        client.settimeout(300)
        
        # Receive folder name (read until newline)
        data = b""
        while b'\n' not in data:
            chunk = client.recv(1)
            if not chunk:
                break
            data += chunk
        
        if not data:
            print("[-] No data received")
            client.close()
            return
        
        line = data.decode().strip()
        if not line.startswith("FOLDER:"):
            print(f"[-] Invalid: {line}")
            client.close()
            return
        
        folder_name = line.replace("FOLDER:", "")
        print(f"[*] 📁 Folder: {folder_name}")
        
        # Receive file count
        data = b""
        while b'\n' not in data:
            chunk = client.recv(1)
            if not chunk:
                break
            data += chunk
        
        if not data:
            print("[-] No count received")
            client.close()
            return
        
        line = data.decode().strip()
        if not line.startswith("COUNT:"):
            print(f"[-] Invalid count: {line}")
            client.close()
            return
        
        file_count = int(line.replace("COUNT:", ""))
        print(f"[*] 📊 Files: {file_count}")
        
        # Create save folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(SAVE_FOLDER, f"{folder_name}_{timestamp}")
        os.makedirs(save_path, exist_ok=True)
        print(f"[*] 💾 Saving to: {save_path}")
        
        received = 0
        
        # Receive files
        for i in range(file_count):
            try:
                # Receive file header
                data = b""
                while b'\n' not in data:
                    chunk = client.recv(1)
                    if not chunk:
                        break
                    data += chunk
                
                if not data:
                    print("[-] No file header")
                    break
                
                header = data.decode().strip()
                if not header.startswith("FILE:"):
                    print(f"[-] Invalid header: {header}")
                    break
                
                parts = header.replace("FILE:", "").split(":")
                if len(parts) < 2:
                    print(f"[-] Invalid format: {header}")
                    break
                
                rel_path = parts[0]
                file_size = int(parts[1])
                
                filepath = os.path.join(save_path, rel_path)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                filename = os.path.basename(rel_path)
                print(f"\n[*] Receiving: {filename} ({file_size:,} bytes)")
                
                # Receive file data
                received_size = 0
                with open(filepath, 'wb') as f:
                    while received_size < file_size:
                        chunk = client.recv(BUFFER_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        received_size += len(chunk)
                        
                        if file_size > 1024*1024:
                            if received_size % (1024*1024) == 0 or received_size == file_size:
                                progress = (received_size / file_size) * 100
                                print(f"\r   Progress: {received_size:,}/{file_size:,} bytes ({progress:.1f}%)", end='', flush=True)
                
                if received_size == file_size:
                    print(f"\n[+] ✅ Saved: {filename}")
                    received += 1
                else:
                    print(f"\n[-] ⚠️ Incomplete: {filename}")
                    
            except Exception as e:
                print(f"[-] Error receiving file {i+1}: {e}")
                break
        
        print(f"\n[+] ✅ Session complete!")
        print(f"[+] 📊 Received {received}/{file_count} files")
        print(f"[+] 📁 Location: {save_path}")
        print("-"*60)
        client.close()
        
    except Exception as e:
        print(f"[-] Error: {e}")
        try:
            client.close()
        except:
            pass

# ============= MAIN LOOP =============
while True:
    try:
        client, addr = server.accept()
        # Handle each client in separate thread
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()
    except Exception as e:
        print(f"[-] Server error: {e}")
        print("[*] Restarting server...")
        server = create_server()
