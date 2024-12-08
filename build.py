
import PyInstaller.__main__
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'main.py',
    '--name=SchadFlow',
    '--onefile',
    '--windowed',
    '--clean',
    '--add-data=visuals;visuals',
    '--add-data=logic;logic',
    '--add-data=ui;ui',
    '--hidden-import=PySide6.QtCore',
    '--hidden-import=matplotlib',
])