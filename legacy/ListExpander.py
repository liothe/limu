__author__ = 'liothe'
from PyQt5 import QtCore


def expand(i, win):
    if i.expandCheck.isChecked():
        win.setMaximumSize(QtCore.QSize(550, 400))
        win.setMinimumSize(QtCore.QSize(550, 400))
        win.resize(550, 400)
        i.trackList.show()
        i.recentTracksList.show()
    else:
        win.setMaximumSize(QtCore.QSize(350, 212))
        win.setMinimumSize(QtCore.QSize(350, 212))
        win.resize(350, 212)
        i.trackList.hide()
        i.recentTracksList.hide()