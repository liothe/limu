# Gstreamer backend for audio playback
__author__ = 'liothe'

from Playback import TimeConverter
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init(None)


class Player(object):
    def __init__(self):
        self._player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self._player.set_property("video-sink", fakesink)
        self.status = None
        self.media = None

    def set_item(self, filepath):
        self._player.set_property("uri", "file:///" + filepath)
        self.media = filepath
    def get_item(self):
        return self.media

    def play_item(self):
        if self.status == "playing":
            self._player.set_state(Gst.State.PAUSED)
            self.status = "paused"
        else:
            self._player.set_state(Gst.State.PLAYING)
            self.status = "playing"

    def pause_item(self):
        self._player.set_state(Gst.State.PAUSED)
        self.status = "paused"

    def stop_item(self):
        self._player.set_state(Gst.State.READY)
        self._player.set_state(Gst.State.NULL)
        self.status = "stopped"

    def track_item_pos(self):
        formatter = Gst.Format.TIME
        position = self._player.query_position(formatter)
        duration = self._player.query_duration(formatter)
        seconds_position = position[1] / 1000000000
        seconds_duration = duration[1] / 1000000000
        # converts seconds to hour,minutes & seconds for the total duration
        duration = int(seconds_duration)
        total_dur = TimeConverter.convert(duration)
        # same, but for the current position
        position = int(seconds_position)
        current_pos = TimeConverter.convert(position)
        # and now to calculate time left, while also converting
        time_left = TimeConverter.calculate_time_left(position, duration)

        pd = (current_pos, total_dur, time_left, position, duration)
        return pd

    def change_item_pos(self, value):
        formatter = Gst.Format.TIME
        seeker = Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT
        seeker_pos = value * Gst.SECOND
        self._player.seek_simple(formatter, seeker, seeker_pos)

    def reset(self):
        self.stop_item()
        formatter = Gst.Format.TIME
        seeker = Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT
        seeker_pos = 0 * Gst.SECOND
        self._player.seek_simple(formatter, seeker, seeker_pos)
        self._player.set_property("uri", None)
        self.status = None
        self.media = ""