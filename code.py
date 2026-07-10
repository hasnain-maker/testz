#!/usr/bin/env python3
"""
Remote Control Client - Target Machine
Run this on the machine you want to control
"""

import socket
import subprocess
import os
import time
import threading
import sys
import ctypes
import platform

class RemoteControlClient:
    def __init__(self, server_ip='192.168.1.103', port=4444):
        self.server_ip = server_ip
        self.port = port
        self.running = True
        self.screen_on = True
        self.power_on = True
        self.system = platform.system()
        
    def connect(self):
        """Connect to server"""
        while self.running:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.server_ip, self.port))
                print(f"✅ Connected to {self.server_ip}:{self.port}")
                self.handle_commands()
            except Exception as e:
                print(f"⚠️ Connection error: {e}")
                time.sleep(5)
    
    def handle_commands(self):
        """Handle incoming commands"""
        while self.running:
            try:
                data = self.sock.recv(1024).decode()
                if not data:
                    break
                
                print(f"📩 Command: {data}")
                self.execute_command(data)
                
            except Exception as e:
                print(f"⚠️ Error: {e}")
                break
    
    def execute_command(self, command):
        """Execute received command"""
        if command == 'power_off':
            self.power_off()
        elif command == 'power_on':
            self.power_on_func()
        elif command == 'screen_off':
            self.screen_off()
        elif command == 'screen_on':
            self.screen_on_func()
        elif command == 'slow_anim':
            self.slow_animation()
        elif command == 'fast_anim':
            self.fast_animation()
        elif command == 'matrix_anim':
            self.matrix_effect()
        elif command == 'rainbow_anim':
            self.rainbow_effect()
        elif command == 'emergency_stop':
            self.emergency_stop()
        else:
            print(f"⚠️ Unknown command: {command}")
    
    def power_off(self):
        """Turn off screen/display"""
        self.power_on = False
        if self.system == 'Windows':
            # Windows: Turn off display
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
        else:
            # Linux: Use xset
            os.system('xset dpms force off')
        print("🔴 Power OFF")
    
    def power_on_func(self):
        """Turn on screen"""
        self.power_on = True
        if self.system == 'Windows':
            # Simulate keypress to wake screen
            ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)  # Shift key
            ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)
        else:
            os.system('xset dpms force on')
        print("🟢 Power ON")
    
    def screen_off(self):
        """Blank screen with animation"""
        self.screen_on = False
        self.slow_animation()
        print("⬛ Screen OFF")
    
    def screen_on_func(self):
        """Restore screen"""
        self.screen_on = True
        self.clear_screen()
        print("⬜ Screen ON")
    
    def slow_animation(self):
        """Slow animation effect"""
        print("🌀 Starting slow animation...")
        try:
            for i in range(10):
                os.system('cls' if self.system == 'Windows' else 'clear')
                print("=" * i + "█" + "=" * (20-i))
                print(f"Slow Animation {i+1}/10")
                time.sleep(0.5)
        except:
            pass
    
    def fast_animation(self):
        """Fast flashing animation"""
        print("⚡ Starting fast animation...")
        for _ in range(20):
            os.system('cls' if self.system == 'Windows' else 'clear')
            print("█" * 40)
            time.sleep(0.1)
            os.system('cls' if self.system == 'Windows' else 'clear')
            print(" " * 40)
            time.sleep(0.1)
    
    def matrix_effect(self):
        """Matrix-style effect"""
        print("💀 Matrix Effect Activated!")
        chars = "01"
        try:
            for _ in range(30):
                line = ''.join(chars[ord(c) % 2] for c in str(time.time()))
                print(line)
                time.sleep(0.05)
        except:
            pass
    
    def rainbow_effect(self):
        """Rainbow color effect"""
        print("🎨 Rainbow Effect!")
        colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
        for i in range(20):
            color = colors[i % len(colors)]
            print(f"{color}█" * 40 + '\033[0m')
            time.sleep(0.2)
    
    def clear_screen(self):
        """Clear screen"""
        os.system('cls' if self.system == 'Windows' else 'clear')
    
    def emergency_stop(self):
        """Emergency stop - exit"""
        print("🆘 EMERGENCY STOP!")
        self.running = False
        sys.exit(0)

if __name__ == "__main__":
    print("=" * 50)
    print("🎯 Remote Control Client")
    print("=" * 50)
    
    # Get server IP
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = input("📡 Enter Kali Linux IP: ").strip()
        if not server_ip:
            server_ip = "127.0.0.1"
    
    print(f"🔗 Connecting to {server_ip}:4444")
    client = RemoteControlClient(server_ip)
    
    try:
        client.connect()
    except KeyboardInterrupt:
        print("\n👋 Disconnected")
