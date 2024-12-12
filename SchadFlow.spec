# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('c:\\Users\\anase\\Semester 5 Project\\SchadFlow\\visuals', 'visuals'), ('c:\\Users\\anase\\Semester 5 Project\\SchadFlow\\logic', 'logic'), ('c:\\Users\\anase\\Semester 5 Project\\SchadFlow\\ui', 'ui')],
    hiddenimports=['PySide6.QtCore', 'matplotlib'],
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
    name='SchadFlow',
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
    icon=['c:\\Users\\anase\\Semester 5 Project\\SchadFlow\\os project icon.ico'],
)
