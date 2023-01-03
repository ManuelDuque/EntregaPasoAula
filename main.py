import sys
from PyQt5.QtWidgets import QApplication
from src.qtwindow import QtWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QtWindow()
    app.exec_()