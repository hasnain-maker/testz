import socket
import os
import time
from datetime import datetime

LISTEN_IP = '0.0.0.0'
LISTEN_PORT = 9998
SAVE_FOLDER = "received_folders"
BUFFER_SIZE = 8192

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

print("="*60)
print("KALI RECEIVER - LARGE FILE SUPPORT")
print("="*60)
print(f"Listening: {LISTEN_IP}:{LISTEN_PORT}")
print(f"Saving to: {SAVE_FOLDER}")
print(f"Buffer: {BUFFER_SIZE} bytes")
print("="*60)

# Create server
server = None
while True:
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # Keep connection alive
        server.bind((LISTEN_IP, LISTEN_PORT))
        server.listen(5)
        print("[*] ✅ Server started successfully!")
        break
    except Exception as e:
        print(f"[-] Error: {e}")
        print("[*] Retrying in 5 seconds...")
        time.sleep(5)

print("[*] Waiting for connections...\n")

while True:
    try:
        client, addr = server.accept()
        print(f"\n[+] Connection from: {addr}")
        
        # Set longer timeout for large files
        client.settimeout(300)  # 5 minutes timeout
        
        # Get folder name
        try:
            data = client.recv(1024).decode().strip()
            if not data.startswith("FOLDER:"):
                print(f"[-] Invalid data: {data[:50]}")
                client.close()
                continue
            folder_name = data.replace("FOLDER:", "")
            print(f"[*] 📁 Folder: {folder_name}")
        except socket.timeout:
            print("[-] Timeout receiving folder name")
            client.close()
            continue
        
        # Get file count
        try:
            data = client.recv(1024).decode().strip()
            if not data.startswith("COUNT:"):
                print("[-] Invalid count")
                client.close()
                continue
            file_count = int(data.replace("COUNT:", ""))
            print(f"[*] 📊 Files: {file_count}")
        except socket.timeout:
            print("[-] Timeout receiving file count")
            client.close()
            continue
        
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
                header_data = b""
                while b"\n" not in header_data:
                    chunk = client.recv(1)
                    if not chunk:
                        break
                    header_data += chunk
                
                header = header_data.decode().strip()
                if not header.startswith("FILE:"):
                    print(f"[-] Invalid file header: {header[:50]}")
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
                
                # Receive file data with progress
                received_size = 0
                with open(filepath, 'wb') as f:
                    while received_size < file_size:
                        chunk = client.recv(BUFFER_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        received_size += len(chunk)
                        
                        # Show progress for large files
                        if file_size > 1024*1024:
                            if received_size % (1024*1024) == 0 or received_size == file_size:
                                progress = (received_size / file_size) * 100
                                print(f"\r   Progress: {received_size:,}/{file_size:,} bytes ({progress:.1f}%)", end='', flush=True)
                
                if received_size == file_size:
                    print(f"\n[+] ✅ Saved: {filename}")
                    received += 1
                else:
                    print(f"\n[-] ⚠️ Incomplete: {filename} ({received_size:,}/{file_size:,})")
                    
            except socket.timeout:
                print(f"[-] Timeout receiving file {i+1}")
                break
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
