"""
Build script for AI Chat Tool
Creates standalone exe with all dependencies and custom robot icon
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required packages if not present"""
    packages = [
        ("PyInstaller", "pyinstaller"),
        ("PIL", "pillow"),
    ]
    
    for module_name, pip_name in packages:
        try:
            __import__(module_name)
            print(f"✓ {pip_name} already installed")
        except ImportError:
            print(f"Installing {pip_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            print(f"✓ {pip_name} installed")

def generate_icon():
    """Generate robot icon for the application"""
    print("\n" + "="*50)
    print("Generating robot icon...")
    print("="*50 + "\n")
    
    from generate_icon import generate_robot_icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robot_icon.ico")
    generate_robot_icon(output_path=icon_path)
    return icon_path

def build_exe(icon_path):
    """Build the executable with custom icon"""
    print("\n" + "="*50)
    print("Building AI Chat Tool...")
    print("="*50 + "\n")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=AIChat-xiaomimimoapi",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        f"--icon={icon_path}",
        # Include all necessary packages
        "--hidden-import=customtkinter",
        "--hidden-import=requests",
        "--hidden-import=dotenv",
        "--hidden-import=PIL",
        "--hidden-import=PIL._tkinter_finder",
        # Collect all customtkinter data
        "--collect-all=customtkinter",
        # Main script
        "ai_chat_simple.py"
    ]
    
    print("Running PyInstaller...")
    print(" ".join(cmd))
    print()
    
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    if result.returncode == 0:
        print("\n" + "="*50)
        print("✓ Build successful!")
        print("="*50)
        print(f"\nExecutable location: dist/AIChat-xiaomimimoapi.exe")
        print(f"Icon used: {icon_path}")
        print("\nNote: API config will be saved to:")
        print("  %USERPROFILE%\\.aichat_config.env")
    else:
        print("\n✗ Build failed!")
        return False
    
    return True

if __name__ == "__main__":
    install_dependencies()
    icon_path = generate_icon()
    build_exe(icon_path)
