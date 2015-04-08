# -*- coding: utf-8 -*-
# Main file
__author__ = 'liothe'
__version__ = '0.3.2'
import sys
import os
from PyQt5.QtWidgets import QApplication
# Passing arguments
import argparse
parser = argparse.ArgumentParser(description="Possible arguments to LiMu.")
parser.add_argument("-i", nargs="?", help="start limu with a track or folder", default=None)

# Init Application
qapp = QApplication(sys.argv)
from Interface.MainHandler import Application
app = Application(__version__)

args = parser.parse_args()
if args.i is not None:
    if os.path.isfile(args.i):
        app.choose_track(args.i)
    else:
        app.choose_directory(args.i)

# Show GUI / Start the application
if __name__ == "__main__":
    app.window.show()
    sys.exit(qapp.exec_())
