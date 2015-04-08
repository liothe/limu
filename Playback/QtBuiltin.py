# Qts' Builtin backend for Audio playback
__author__ = 'liothe'

from Playback import TimeConverter
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget

video_filter = (".mkv", ".mp4", ".avi", ".wma", ".ogv", ".mpg", ".mpeg")


class Player(object):
    def __init__(self):
        self._player = QMediaPlayer()
        self.video = QVideoWidget()
        self.status = None
        self.media = None

    def set_item(self, filepath):
        is_video = self.check_video(filepath)
        item = QMediaContent(QUrl.fromLocalFile(filepath))
        self._player.setMedia(item)
        if is_video is True:
            self.video.setEnabled(True)
            self._player.setVideoOutput(self.video)
            self.video.setWindowTitle(filepath)
            self.video.show()
        else:
            self.video.setEnabled(False)
            self.video.hide()
        self.media = filepath

    def get_item(self):
        return self.media

    def play_item(self):
        if self.status == "playing":
            self._player.pause()
            self.status = "paused"
        else:
            self._player.play()
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
        self._player.setMedia(QMediaContent(QUrl.fromLocalFile(None)))
        self.status = None
        self.media = ""

    @staticmethod
    def check_video(file):
        video = False
        for end in video_filter:
            if file.lower().endswith(end) is True:
                video = True
        return video