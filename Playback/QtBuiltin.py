# Qts' Builtin backend for Audio playback
__author__ = 'liothe'

from Playback import TimeConverter
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QMouseEvent

'''App Settings'''
from ConfigHandler import Settings
config = Settings.get()

video_filter = config["VideoFiles"]


class Player(QMediaPlayer):
    def __init__(self):
        QMediaPlayer.__init__(self)
        self.video = VideoPlayer()
        self.status = None
        self.media = None

    def set_item(self, filepath):
        is_video = self.check_video(filepath)
        item = QMediaContent(QUrl.fromLocalFile(filepath))
        self.setMedia(item)
        if is_video is True:
            self.video.setEnabled(True)
            self.setVideoOutput(self.video)
            self.video.setWindowTitle(filepath)
        else:
            self.video.setEnabled(False)
            self.video.hide()
        self.media = filepath

    def get_item(self):
        return self.media

    def play_item(self):
        if self.status == "playing":
            self.pause()
            self.status = "paused"
        else:
            self.play()
            self.status = "playing"

    def pause_item(self):
        self.pause()
        self.status = "paused"

    def stop_item(self):
        self.stop()
        self.status = "stopped"

    def track_item_pos(self):
        position = self.position() / 1000
        duration = self.duration() / 1000
        total_dur = TimeConverter.convert(int(duration))
        current_pos = TimeConverter.convert(int(position))
        time_left = TimeConverter.calculate_time_left(int(position), int(duration))

        pd = (current_pos, total_dur, time_left, int(position), int(duration))
        return pd

    def change_item_pos(self, value):
        self.setPosition(float(value) * 1000)

    def reset(self):
        self.stop_item()
        self.setPosition(float(0) * 1000)
        self.setMedia(QMediaContent(QUrl.fromLocalFile(None)))
        self.status = None
        self.media = ""

    @staticmethod
    def check_video(file):
        video = False
        for video_format in video_filter:
            if file.lower().endswith(video_format) is True:
                video = True
                break
        return video


class VideoPlayer(QVideoWidget):
    def __init__(self):
        QVideoWidget.__init__(self)

    def mouseDoubleClickEvent(self, QMouseEvent):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.setFullScreen(True)
