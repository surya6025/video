# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for JarvisX
Builds a Windows executable with all dependencies
"""

import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent

# Define the main script
main_script = str(project_root / 'main.py')

# Define data files to include
data_files = [
    # Include the entire project structure
    (str(project_root / 'core'), 'core'),
    (str(project_root / 'ui'), 'ui'),
    (str(project_root / 'skills'), 'skills'),
    (str(project_root / 'tools'), 'tools'),
    
    # Include configuration files
    (str(project_root / '.env.template'), '.'),
    (str(project_root / 'README.md'), '.'),
    (str(project_root / 'requirements.txt'), '.'),
    
    # Include test files (optional, can be removed for production)
    (str(project_root / 'tests'), 'tests'),
    (str(project_root / 'pytest.ini'), '.'),
    
    # Create necessary directories
    ('', 'logs'),
    ('', 'temp'),
    ('', 'ui/assets'),
]

# Define hidden imports (modules that PyInstaller might miss)
hidden_imports = [
    # Core modules
    'core.logging_utils',
    'core.models',
    'core.memory',
    'core.permissions',
    'core.router',
    'core.assistant',
    'core.io',
    'core.app',
    'core.updater',
    'core.evaluator',
    
    # UI modules
    'ui.chat_window',
    'ui.widgets',
    
    # Skills
    'skills.base_skill',
    'skills.nlp',
    'skills.ml',
    'skills.data_science',
    'skills.data_engineering',
    'skills.analytics',
    'skills.automation',
    'skills.cybersecurity',
    'skills.system_control',
    'skills.ui_ux',
    'skills.web_search',
    
    # Tools
    'tools.rag_index',
    'tools.viz',
    
    # Third-party libraries
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt5.QtTest',
    'PyQt5.sip',
    'pandas',
    'numpy',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
    'seaborn',
    'sklearn',
    'sklearn.feature_extraction.text',
    'sklearn.linear_model',
    'sklearn.ensemble',
    'sklearn.metrics',
    'sklearn.preprocessing',
    'faiss',
    'loguru',
    'supabase',
    'psycopg2',
    'requests',
    'yaml',
    'pydantic',
]

# Define excluded modules (modules that shouldn't be included)
excludes = [
    'tkinter',
    'test',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
    'email',
    'html',
    'http',
    'urllib',
    'xml',
    'pydoc_data',
    'setuptools',
    'distutils',
    'pip',
    'wheel',
    'pytest',
    'pytest_cov',
    'pytest_html',
]

# Define binary files to include
binaries = []

# Define datas (additional data files)
datas = []

# Analysis configuration
a = Analysis(
    [main_script],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
a.datas = list(set(a.datas))

# PYZ configuration
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# EXE configuration
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JarvisX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'ui/assets' / 'jarvisx.ico') if (project_root / 'ui/assets' / 'jarvisx.ico').exists() else None,
    version_file=None,
    uac_admin=False,
    uac_uiaccess=False,
)

# COLLECT configuration (for directory-based distribution)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JarvisX',
)

# OneFile configuration (alternative to COLLECT)
# Uncomment the following lines to create a single executable file
# exe_onefile = EXE(
#     pyz,
#     a.scripts,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     [],
#     name='JarvisX_OneFile',
#     debug=False,
#     bootloader_ignore_signals=False,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     runtime_tmpdir=None,
#     console=False,
#     disable_windowed_traceback=False,
#     argv_emulation=False,
#     target_arch=None,
#     codesign_identity=None,
#     entitlements_file=None,
#     icon=str(project_root / 'ui/assets' / 'jarvisx.ico') if (project_root / 'ui/assets' / 'jarvisx.ico').exists() else None,
# )

# Build instructions:
# 1. Install PyInstaller: pip install pyinstaller
# 2. Run: pyinstaller jarvisx.spec
# 3. Find output in dist/JarvisX/ directory
# 4. For one-file build, uncomment exe_onefile section and run: pyinstaller --onefile jarvisx.spec