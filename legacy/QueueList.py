__author__ = 'liothe'
import PyQt5

def show_hide(i, win):
    if i.showhidequeueCheck.isChecked():
        win.setMaximumSize(PyQt5.QtCore.QSize(350, 390))
        win.setMinimumSize(PyQt5.QtCore.QSize(350, 390))
        win.resize(350, 390)
        i.trackList.show()
    else:
        win.setMaximumSize(PyQt5.QtCore.QSize(350, 200))
        win.setMinimumSize(PyQt5.QtCore.QSize(350, 200))
        win.resize(350, 200)
        i.trackList.hide()