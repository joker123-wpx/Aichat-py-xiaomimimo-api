# -*- coding: utf-8 -*-
import os
import sys
import shutil
import zipfile
import tempfile
import ctypes
import winreg

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_shortcut(target, shortcut_path, icon_path=None, description=""):
    """Create Windows shortcut using PowerShell"""
    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target}"
{f'$Shortcut.IconLocation = "{icon_path}"' if icon_path else ''}
$Shortcut.Description = "{description}"
$Shortcut.Save()
"""
    import subprocess
    subprocess.run(["powershell", "-Command", ps_script], capture_output=True)

def main():
    print("="*50)
    print("  AI Chat Installer")
    print("="*50)
    print()
    
    # Default install path
    default_path = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "AIChat")
    
    print(f"Default install location: {default_path}")
    user_path = input("Press Enter to accept or type new path: ").strip()
    install_path = user_path if user_path else default_path
    
    print(f"\nInstalling to: {install_path}")
    
    # Create directory
    os.makedirs(install_path, exist_ok=True)
    
    # Extract files from embedded zip
    script_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    
    # Copy main exe
    src_exe = os.path.join(script_dir, "_app", "AIChat-xiaomimimoapi.exe")
    src_icon = os.path.join(script_dir, "_app", "robot_icon.ico")
    
    if not os.path.exists(src_exe):
        # Try extracting from zip embedded in exe
        print("Extracting files...")
        
    dst_exe = os.path.join(install_path, "AIChat-xiaomimimoapi.exe")
    dst_icon = os.path.join(install_path, "robot_icon.ico")
    
    shutil.copy2(src_exe, dst_exe)
    if os.path.exists(src_icon):
        shutil.copy2(src_icon, dst_icon)
    
    print("Creating shortcuts...")
    
    # Desktop shortcut
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    create_shortcut(dst_exe, os.path.join(desktop, "AI Chat.lnk"), dst_icon, "AI Chat Tool")
    
    # Start menu shortcut
    start_menu = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
    create_shortcut(dst_exe, os.path.join(start_menu, "AI Chat.lnk"), dst_icon, "AI Chat Tool")
    
    print()
    print("="*50)
    print("  Installation Complete!")
    print("="*50)
    print(f"\nInstalled to: {install_path}")
    print("Shortcuts created on Desktop and Start Menu")
    print()
    
    launch = input("Launch AI Chat now? (Y/n): ").strip().lower()
    if launch != 'n':
        os.startfile(dst_exe)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
