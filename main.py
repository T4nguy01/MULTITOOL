import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from config_manager import ConfigManager

VERSION_LOCALE = open("version.txt").read().strip()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Multitool")
    app.setApplicationVersion(VERSION_LOCALE)
    app.setOrganizationName("T4nguy & Gaëtan")
    
    config = ConfigManager("config.json")
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
