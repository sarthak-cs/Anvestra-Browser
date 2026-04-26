import os
import sys

flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
extflags = [
    "--disable-features=RendererCodeIntegrity",
    "--disable-direct-composition"
]
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(
    [flag for flag in [flags, *extflags] if flag]
)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from browser_window import BrowserWindow

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("images/favicon.ico"))
app.setStyle("Fusion")  
app.setStyleSheet("""
QMainWindow {
    background-color: #0f172a;
}

QToolBar {
    background: #1e293b;
    spacing: 8px;
    padding: 6px;
}

QToolButton {
    background: #334155;
    font-size: 15px;
    border-radius: 8px;
    padding: 6px;
    color: white;
}

QToolButton:hover {
    background: #475569;
}

QLineEdit {
    background: #334155;
    border-radius: 10px;
    padding: 8px;
    color: white;
    font-size: 14px;
}

QTabBar::tab {
    background: #1e293b;
    padding: 10px 20px;
    border-radius: 8px;
    margin: 2px;
    color: white;
}

QTabBar::tab:selected {
    background: #00d4ff;
    color: black;
}
""")
window = BrowserWindow()
window.show()
sys.exit(app.exec())