import sys
from PyQt5.QtWidgets import QApplication
from src.ui import Window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    app.exec_()