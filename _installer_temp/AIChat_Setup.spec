# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\31243\\Desktop\\001\\ai_tool\\_installer_temp\\installer_main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\31243\\Desktop\\001\\ai_tool\\_installer_temp\\_app', '_app')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AIChat_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\31243\\Desktop\\001\\ai_tool\\robot_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AIChat_Setup',
)
