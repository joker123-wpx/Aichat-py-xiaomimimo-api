# -*- coding: utf-8 -*-
"""
Create a simple installer using Python
Creates a self-extracting installer executable
"""

import subprocess
import sys
import os
import shutil
import zipfile

def create_installer():
    """Create installer package"""
    print("="*50)
    print("Creating AI Chat Installer...")
    print("="*50 + "\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    installer_dir = os.path.join(base_dir, "installer_output")
    
    # Create installer output directory
    os.makedirs(installer_dir, exist_ok=True)
    
    exe_path = os.path.join(dist_dir, "AIChat-xiaomimimoapi.exe")
    icon_path = os.path.join(base_dir, "robot_icon.ico")
    
    if not os.path.exists(exe_path):
        print("Error: AIChat-xiaomimimoapi.exe not found! Run build.py first.")
        return False
    
    # Create installer script
    installer_script = '''# -*- coding: utf-8 -*-
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
    default_path = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\\\"), "AIChat")
    
    print(f"Default install location: {default_path}")
    user_path = input("Press Enter to accept or type new path: ").strip()
    install_path = user_path if user_path else default_path
    
    print(f"\\nInstalling to: {install_path}")
    
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
    print(f"\\nInstalled to: {install_path}")
    print("Shortcuts created on Desktop and Start Menu")
    print()
    
    launch = input("Launch AI Chat now? (Y/n): ").strip().lower()
    if launch != 'n':
        os.startfile(dst_exe)
    
    input("\\nPress Enter to exit...")

if __name__ == "__main__":
    main()
'''
    
    # Create temp directory for installer build
    temp_dir = os.path.join(base_dir, "_installer_temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create _app folder with files
    app_dir = os.path.join(temp_dir, "_app")
    os.makedirs(app_dir, exist_ok=True)
    
    print("Copying application files...")
    shutil.copy2(exe_path, os.path.join(app_dir, "AIChat-xiaomimimoapi.exe"))
    if os.path.exists(icon_path):
        shutil.copy2(icon_path, os.path.join(app_dir, "robot_icon.ico"))
    
    # Write installer script
    installer_py = os.path.join(temp_dir, "installer_main.py")
    with open(installer_py, 'w', encoding='utf-8') as f:
        f.write(installer_script)
    
    print("Building installer executable...")
    
    # Build installer exe with PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=AIChat_Setup",
        "--onedir",
        "--console",
        "--noconfirm",
        "--clean",
        f"--icon={icon_path}",
        f"--add-data={app_dir};_app",
        "--distpath=" + installer_dir,
        installer_py
    ]
    
    result = subprocess.run(cmd, cwd=temp_dir)
    
    # Cleanup temp
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    if result.returncode == 0:
        print("\n" + "="*50)
        print("✓ Installer created successfully!")
        print("="*50)
        print(f"\nInstaller location: {os.path.join(installer_dir, 'AIChat_Setup')}")
        print("\nTo distribute, zip the AIChat_Setup folder or use the exe directly.")
        return True
    else:
        print("\n✗ Installer creation failed!")
        return False


if __name__ == "__main__":
    create_installer()
