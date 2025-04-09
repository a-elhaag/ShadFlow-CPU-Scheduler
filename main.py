import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setApplicationName("ShadFlow CPU Scheduler")
    dark_palette = QPalette()
    dark_color = QColor(45, 45, 45)
    nearly_black = QColor(35, 35, 35)
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

    window = MainWindow()
    window.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        print("An unexpected error occurred:", e)
        sys.exit(1)
