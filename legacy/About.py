__author__ = 'liothe'

from PyQt5.QtWidgets import QDialog, QLabel, QWidget
from PyQt5.QtCore import QRect


def dialog(win, ver):
    d = QDialog(win)
    d.setWindowTitle("About LiMu")
    container = QWidget(d)
    container.setGeometry(QRect(0, 0, 200, 80))
    about_text = QLabel(container)
    about_text.setText("the Liothe Music Player\nCreated by: Liothe\n\nVersion: " + ver)
    d.show()