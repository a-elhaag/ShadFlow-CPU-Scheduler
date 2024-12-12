import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setApplicationName("ShadFlow CPU Scheduler")
    # app.setWindowIcon(QIcon("icon.png"))  # Uncomment if you have an icon

    # Set a dark palette
    dark_palette = QPalette()
    dark_color = QColor(45, 45, 45)
    nearly_black = QColor(35, 35, 35)
    medium_grey = QColor(90, 90, 90)
    light_grey = QColor(160, 160, 160)
    white = QColor(255, 255, 255)
    highlight_color = QColor(142, 68, 173)

    dark_palette.setColor(QPalette.Window, dark_color)
    dark_palette.setColor(QPalette.WindowText, white)
    dark_palette.setColor(QPalette.Base, nearly_black)
    dark_palette.setColor(QPalette.AlternateBase, dark_color)
    dark_palette.setColor(QPalette.ToolTipBase, white)
    dark_palette.setColor(QPalette.ToolTipText, white)
    dark_palette.setColor(QPalette.Text, white)
    dark_palette.setColor(QPalette.Button, dark_color)
    dark_palette.setColor(QPalette.ButtonText, white)
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Highlight, highlight_color)
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)

    app.setPalette(dark_palette)

    # Optionally, you can also set a fusion style for a more consistent look:
    # from PySide6.QtWidgets import QStyleFactory
    # app.setStyle(QStyleFactory.create("Fusion"))

    window = MainWindow()
    window.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        print("An unexpected error occurred:", e)
        sys.exit(1)
