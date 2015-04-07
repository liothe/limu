# Qts' Builtin backend for Audio playback
__author__ = 'liothe'

from Playback import TimeConverter
from PyQt5 import QtMultimedia
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget


class Player(object):
    def __init__(self):
        self._player = QtMultimedia.QMediaPlayer()
        self.video = QVideoWidget()
        self.status = None
        self.media = None

    def set_item(self, filepath):
        item = QtMultimedia.QMediaContent(QUrl.fromLocalFile(filepath))
        self._player.setMedia(item)
        self._player.setVideoOutput(self.video)
        self.media = filepath

    def get_item(self):
        return self.media

    def play_item(self):
        if self.status == "playing":
            self._player.pause()
            self.status = "paused"
        else:
            self._player.play()
            self.video.show()
            self.status = "playing"

    def pause_item(self):
        self._player.pause()
        self.status = "paused"

    def stop_item(self):
        self._player.stop()
        self.status = "stopped"

    def track_item_pos(self):
        position = self._player.position() / 1000
        duration = self._player.duration() / 1000
        total_dur = TimeConverter.convert(int(duration))
        current_pos = TimeConverter.convert(int(position))
        time_left = TimeConverter.calculate_time_left(int(position), int(duration))

        pd = (current_pos, total_dur, time_left, int(position), int(duration))
        return pd

    def change_item_pos(self, value):
        self._player.setPosition(float(value) * 1000)

    def reset(self):
        self.stop_item()
        self._player.setPosition(float(0) * 1000)
        self._player.setMedia(QtMultimedia.QMediaContent(QUrl.fromLocalFile(None)))
        self.status = None
        self.media = ""
