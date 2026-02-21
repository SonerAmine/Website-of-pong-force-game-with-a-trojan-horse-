# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\PC\\Desktop\\pong_project\\pong_force\\assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PongForce',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\PC\\Desktop\\pong_project\\pong_force\\version_info.txt',
    icon=['C:\\Users\\PC\\Desktop\\pong_project\\pong_force\\assets\\ping-pong.ico'],
    manifest='C:\\Users\\PC\\Desktop\\pong_project\\pong_force\\uac_admin.manifest',
)
