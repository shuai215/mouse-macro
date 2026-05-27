# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
)


project_root = Path(SPECPATH)

pyqt6_binaries = collect_dynamic_libs("PyQt6")
pyqt6_datas = collect_data_files(
    "PyQt6",
    includes=[
        "Qt6/plugins/platforms/*",
        "Qt6/plugins/styles/*",
        "Qt6/plugins/iconengines/*",
        "Qt6/plugins/imageformats/*",
        "Qt6/translations/*",
    ],
)

qfluent_datas = collect_data_files("qfluentwidgets")
qfluent_hiddenimports = collect_submodules("qfluentwidgets")


a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=pyqt6_binaries,
    datas=pyqt6_datas + qfluent_datas,
    hiddenimports=[
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        *qfluent_hiddenimports,
    ],
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
    [],
    name="mouse-macro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="mouse-macro",
)
