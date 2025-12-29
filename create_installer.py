# -*- coding: utf-8 -*-
"""
Create a single-file installer for AI Chat
"""

import subprocess
import sys
import os
import shutil
import base64
import zipfile
import io

def create_installer():
    print("="*50)
    print("Creating AI Chat Installer...")
    print("="*50 + "\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "dist")
    installer_dir = os.path.join(base_dir, "installer_output")
    os.makedirs(installer_dir, exist_ok=True)
    
    exe_path = os.path.join(dist_dir, "AIChat-xiaomimimoapi.exe")
    icon_path = os.path.join(base_dir, "robot_icon.ico")
    
    if not os.path.exists(exe_path):
        print("Error: Run build.py first!")
        return False
    
    print("Compressing application files...")
    
    # Create zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe_path, "AIChat-xiaomimimoapi.exe")
        if os.path.exists(icon_path):
            zf.write(icon_path, "robot_icon.ico")
    
    zip_data = base64.b64encode(zip_buffer.getvalue()).decode('ascii')
    
    print(f"Compressed size: {len(zip_data) // 1024} KB")
    
    # Installer script with embedded data
    installer_code = '''# -*- coding: utf-8 -*-
import os
import sys
import shutil
import zipfile
import base64
import io
import subprocess
import tempfile

# Embedded application data (base64 encoded zip)
APP_DATA = """''' + zip_data + '''"""

def create_shortcut(target, shortcut_path, icon_path=None, description=""):
    """Create Windows shortcut"""
    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target}'
"""
    if icon_path:
        ps_script += f"$Shortcut.IconLocation = '{icon_path}'\\n"
    ps_script += f"""$Shortcut.Description = '{description}'
$Shortcut.Save()
"""
    subprocess.run(["powershell", "-Command", ps_script], 
                   capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

def main():
    print()
    print("="*50)
    print("       AI Chat 安装程序")
    print("="*50)
    print()
    
    # Default install path
    local_app = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    default_path = os.path.join(local_app, "AIChat")
    
    print(f"默认安装路径: {default_path}")
    print()
    user_path = input("按 Enter 使用默认路径，或输入新路径: ").strip()
    install_path = user_path if user_path else default_path
    
    print()
    print(f"正在安装到: {install_path}")
    print()
    
    try:
        # Create directory
        os.makedirs(install_path, exist_ok=True)
        
        # Extract files
        print("正在解压文件...")
        zip_data = base64.b64decode(APP_DATA)
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            zf.extractall(install_path)
        
        exe_file = os.path.join(install_path, "AIChat-xiaomimimoapi.exe")
        icon_file = os.path.join(install_path, "robot_icon.ico")
        
        if not os.path.exists(exe_file):
            print("错误: 解压失败!")
            input("按 Enter 退出...")
            return
        
        print("正在创建快捷方式...")
        
        # Desktop shortcut
        desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
        desktop_lnk = os.path.join(desktop, "AI Chat.lnk")
        create_shortcut(exe_file, desktop_lnk, icon_file, "AI Chat Tool")
        
        # Start menu shortcut
        start_menu = os.path.join(os.environ["APPDATA"], 
                                  "Microsoft", "Windows", "Start Menu", "Programs")
        start_lnk = os.path.join(start_menu, "AI Chat.lnk")
        create_shortcut(exe_file, start_lnk, icon_file, "AI Chat Tool")
        
        # Create uninstaller
        uninstall_bat = os.path.join(install_path, "uninstall.bat")
        with open(uninstall_bat, 'w', encoding='gbk') as f:
            f.write('@echo off\\n')
            f.write('echo 正在卸载 AI Chat...\\n')
            f.write('del "' + desktop_lnk + '" 2>nul\\n')
            f.write('del "' + start_lnk + '" 2>nul\\n')
            f.write('rd /s /q "' + install_path + '"\\n')
            f.write('echo 卸载完成!\\n')
            f.write('pause\\n')
        
        print()
        print("="*50)
        print("       安装完成!")
        print("="*50)
        print()
        print(f"安装位置: {install_path}")
        print("已创建桌面快捷方式和开始菜单快捷方式")
        print()
        
        launch = input("现在启动 AI Chat? (Y/n): ").strip().lower()
        if launch != 'n':
            os.startfile(exe_file)
            
    except Exception as e:
        print(f"安装错误: {e}")
    
    print()
    input("按 Enter 退出安装程序...")

if __name__ == "__main__":
    main()
'''
    
    # Write installer script
    temp_dir = os.path.join(base_dir, "_installer_temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    installer_py = os.path.join(temp_dir, "setup.py")
    with open(installer_py, 'w', encoding='utf-8') as f:
        f.write(installer_code)
    
    print("Building installer executable...")
    
    # Build single-file installer
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=AIChat_Setup_v1.0",
        "--onefile",
        "--console",
        "--noconfirm",
        "--clean",
        f"--icon={icon_path}",
        f"--distpath={installer_dir}",
        installer_py
    ]
    
    result = subprocess.run(cmd, cwd=temp_dir)
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    if result.returncode == 0:
        installer_exe = os.path.join(installer_dir, "AIChat_Setup_v1.0.exe")
        size_mb = os.path.getsize(installer_exe) / (1024*1024)
        print("\n" + "="*50)
        print("✓ 安装包创建成功!")
        print("="*50)
        print(f"\n安装包位置: {installer_exe}")
        print(f"文件大小: {size_mb:.1f} MB")
        return True
    else:
        print("\n✗ 创建失败!")
        return False

if __name__ == "__main__":
    create_installer()
