# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Mopex – Desktop Expense Manager.

Build a single-folder distribution:
    pyinstaller mopex.spec

The resulting executable is placed in:
    dist/Mopex/Mopex.exe

The app stores user data at  ~/Documents/Mopex/mopex.db  (never inside
this distribution folder), so the build directory can be freely shared,
moved, or zipped without risk of including personal financial data.
"""

import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Collect all submodules from the gui package so they are bundled
hidden_imports = collect_submodules('gui')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],           # No data files needed - DB lives outside the bundle
    hiddenimports=hidden_imports + [
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        'tkinter.colorchooser',
        'sqlite3',
        'csv',
        'datetime',
        'dataclasses',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Mopex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No terminal / console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',  # Uncomment and add an .ico file to set a custom icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Mopex',
)
