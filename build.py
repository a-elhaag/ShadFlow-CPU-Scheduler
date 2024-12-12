import os

import PyInstaller.__main__

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the icon
icon_path = os.path.join(
    current_dir, "os project icon.ico"
)  # Replace with the actual path to your icon

# Running4 PyInstaller to package the app
PyInstaller.__main__.run(
    [
        "main.py",
        "--name=SchadFlow",  # Set the name of the executable
        "--onefile",  # Package into a single executable
        "--windowed",  # Prevents a terminal window from opening with the GUI
        "--clean",  # Cleans up previous build artifacts
        "--add-data={};{}".format(
            os.path.join(current_dir, "visuals"), "visuals"
        ),  # Add visuals folder
        "--add-data={};{}".format(
            os.path.join(current_dir, "logic"), "logic"
        ),  # Add logic folder
        "--add-data={};{}".format(
            os.path.join(current_dir, "ui"), "ui"
        ),  # Add ui folder
        "--hidden-import=PySide6.QtCore",  # Hidden import for PySide6
        "--hidden-import=matplotlib",  # Hidden import for matplotlib
        "--icon={}".format(icon_path),  # Add icon for the executable
    ]
)
