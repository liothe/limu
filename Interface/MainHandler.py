__author__ = 'liothe'
from Interface.BaseGui import Ui_Main
import os
import sys
import time
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QShortcut
import threading
from queue import Queue

'''App Settings'''
import json
config_file = open(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "/settings.conf")
config = json.loads(config_file.read())
config_file.close()
'''Playback related'''
if config['UseGstreamer'] is False:
    try:
        from Playback.QtBuiltin import Player
        print("QtBuiltin used for multimedia playback")
    except ImportError:
        print("QtBuiltin (qt5-multimedia) wasn't found - trying Gstreamer")
        from Playback.Gstreamer import Player
        print("Gstreamer used for multimedia playback")
elif config['UseGstreamer'] is True:
    try:
        from Playback.Gstreamer import Player
        print("Gstreamer used for multimedia playback")
    except ImportError:
        print("Cannot find Gstreamer library, falling back")
        from Playback.QtBuiltin import Player  # Fallback to QtBuiltin if Gstreamer was set but failed
        print("QtBuiltin used for multimedia playback")


''' Optional, for Track information '''
try:
    from stagger import read_tag, NoTagError, FrameWarning, EmptyFrameWarning
except ImportError:
    print("stagger wasn't found. (https://code.google.com/p/stagger/)")
    print("Unable to gather track information from mp3 files'.")

_norX, _norY = config['NormalWidth'], config['NormalHeight']  # Normal GUI X,Y taken from settings.conf
_expX, _expY = config['ExpandedWidth'], config['ExpandedHeight']  # Expanded GUI X,Y taken from settings.conf

queue = Queue()  # For queuing threads
lock = threading.Lock()  # For locking threads

audio_files = (".mp3", ".ogg", ".oga", ".wav", ".flac")
video_files = (".wma", ".mkv", ".mp4", ".avi", ".mpg", ".ogv")


class Application(QMainWindow):
    def __init__(self, version, window=QMainWindow(), player=Player()):
        QMainWindow.__init__(self)
        self.ui = Ui_Main()
        self.window = window
        self.ui.setupUi(window)
        self.player = player
        self.version = version

        # Init Timer
        self.timer = QtCore.QTimer()
        self.timer.start(1000)  # Update every second
        self.timer.timeout.connect(self.track_elapsed)

        # Button icons
        window_icon = QIcon()
        window_icon.addPixmap(QPixmap(os.path.dirname(os.path.realpath(__file__))
                                    + "/images/window/icon.png"), QIcon.Normal, QIcon.Off)
        self.window.setWindowIcon(window_icon)

        self.play_icon = QIcon()
        self.play_icon.addPixmap(QPixmap(os.path.dirname(os.path.realpath(__file__))
                                    + "/images/buttons/play.png"), QIcon.Normal, QIcon.Off)
        self.pause_icon = QIcon()
        self.pause_icon.addPixmap(QPixmap(os.path.dirname(os.path.realpath(__file__))
                                    + "/images/buttons/pause.png"), QIcon.Normal, QIcon.Off)
        self.next_icon = QIcon()
        self.next_icon.addPixmap(QPixmap(os.path.dirname(os.path.realpath(__file__))
                                    + "/images/buttons/next.png"), QIcon.Normal, QIcon.Off)
        self.prev_icon = QIcon()
        self.prev_icon.addPixmap(QPixmap(os.path.dirname(os.path.realpath(__file__))
                                    + "/images/buttons/previous.png"), QIcon.Normal, QIcon.Off)
        self.stop_icon = QIcon()
        self.stop_icon.addPixmap(QPixmap(os.path.dirname(os.path.realpath(__file__))
                                    + "/images/buttons/stop.png"), QIcon.Normal, QIcon.Off)

        # Set buttons
        self.ui.playpauseButton.setIcon(self.play_icon)
        self.ui.nextButton.setIcon(self.next_icon)
        self.ui.previousButton.setIcon(self.prev_icon)
        self.ui.stopButton.setIcon(self.stop_icon)

        # CheckBox for showing / hiding Expanded Lists
        self.ui.expandCheck.stateChanged.connect(self.lists)
        # And for showing / hiding video window
        self.ui.videoCheck.stateChanged.connect(self.video_window)

        # For dragging the slider
        self.was_it_playing = None
        self.ui.TrackSlider.sliderPressed.connect(self.slider_pressed)
        self.ui.TrackSlider.sliderReleased.connect(self.play_when_slider_released)
        self.ui.TrackSlider.sliderMoved.connect(self.player.change_item_pos)

        # Model to hold track list
        self.queueTrackListModel = QStandardItemModel(self.ui.trackList)
        self.ui.trackList.setModel(self.queueTrackListModel)
        self.recentTrackListModel = QStandardItemModel(self.ui.recentTracksList)
        self.ui.recentTracksList.setModel(self.recentTrackListModel)
        self.ui.trackList.doubleClicked.connect(self.choose_track_from_queue)
        self.ui.recentTracksList.doubleClicked.connect(self.choose_track_from_recent)

        self.ui.trackList.hide()  # we start the list hidden
        self.ui.recentTracksList.hide()  # likewise

        # Connect GUI buttons
        self.ui.playpauseButton.clicked.connect(self.play_track)  # Play / Pause button
        self.ui.stopButton.clicked.connect(self.stop_track)  # Stop button
        self.ui.nextButton.clicked.connect(self.next_track)  # Next button
        self.ui.previousButton.clicked.connect(self.prev_track)  # Next button

        self.ui.actionQuit.triggered.connect(sys.exit)  # Quit from menu
        self.ui.actionOpen.triggered.connect(self.choose_track)  # Open single item from menu
        self.ui.actionOpen_Several.triggered.connect(self.choose_tracks)  # Open several items from menu
        self.ui.actionOpen_Directory.triggered.connect(self.choose_directory)  # Open a directory from menu
        self.ui.actionAbout_LiMu.triggered.connect(self.about_dialog)

        # Keyboard shortcuts
        self.shortcut_next_track = QShortcut(QKeySequence("Right"), self.window)
        self.shortcut_next_track.activated.connect(self.next_track)
        self.shortcut_prev_track = QShortcut(QKeySequence("Left"), self.window)
        self.shortcut_prev_track.activated.connect(self.prev_track)
        self.shortcut_play_track = QShortcut(QKeySequence("Up"), self.window)
        self.shortcut_play_track.activated.connect(self.play_track)
        self.shortcut_stop_track = QShortcut(QKeySequence("Down"), self.window)
        self.shortcut_stop_track.activated.connect(self.stop_track)
        self.shortcut_open_folder = QShortcut(QKeySequence("Ctrl+O"), self.window)
        self.shortcut_open_folder.activated.connect(self.choose_directory)
        self.shortcut_open_track = QShortcut(QKeySequence("Ctrl+I"), self.window)
        self.shortcut_open_track.activated.connect(self.choose_track)
        self.shortcut_open_tracks = QShortcut(QKeySequence("Ctrl+L"), self.window)
        self.shortcut_open_tracks.activated.connect(self.choose_tracks)
        self.shortcut_quit = QShortcut(QKeySequence("Ctrl+Q"), self.window)
        self.shortcut_quit.activated.connect(sys.exit)

        # Starts expanded if set in settings.conf
        if config['Expanded'] is True:
            self.ui.expandCheck.nextCheckState()
            self.window.setMaximumSize(QSize(_expX, _expY))
            self.window.setMinimumSize(QSize(_expX, _expY))
            self.window.resize(_expX, _expY)
            self.ui.trackList.show()
            self.ui.recentTracksList.show()

        # Stuck Counter ( A BUG )
        self.stuck_counter = 0

    def lists(self):
        if self.ui.expandCheck.isChecked():
            self.window.setMaximumSize(QSize(_expX, _expY))
            self.window.setMinimumSize(QSize(_expX, _expY))
            self.window.resize(_expX, _expY)
            self.ui.trackList.show()
            self.ui.recentTracksList.show()
        else:
            self.window.setMaximumSize(QSize(_norX, _norY))
            self.window.setMinimumSize(QSize(_norX, _norY))
            self.window.resize(_norX, _norY)
            self.ui.trackList.hide()
            self.ui.recentTracksList.hide()

    def video_window(self):
        self.check_video()
        if self.player.video.isEnabled():
            if self.ui.videoCheck.isChecked():
                self.player.video.show()
            else:
                self.player.video.hide()

    def check_video(self):
        if self.player.get_item() is not None:
            video = False
            for v in video_files:
                if self.player.get_item().lower().endswith(v):
                    self.ui.videoCheck.setEnabled(True)
                    video = True
                    self.player.video.setEnabled(True)
                    self.player.setVideoOutput(self.player.video)
                    self.player.video.setWindowTitle(self.player.get_item())

            if video is False:
                self.ui.videoCheck.setChecked(False)
                self.ui.videoCheck.setEnabled(False)
                self.player.video.setEnabled(False)

    def slider_pressed(self):
        if self.player.status == "playing":
            self.play_track()
            self.was_it_playing = True
        else:
            self.was_it_playing = False

    def play_when_slider_released(self):
        if self.was_it_playing is True:
            self.play_track()

    def choose_track_from_queue(self, chosen):
        self.player.stop_item()
        if self.player.get_item() is not None:
            self.current_to_recent()
        location = chosen.data(1)
        self.player.set_item(location)
        print("loaded: " + self.player.get_item())
        location = chosen.data(1)
        self.queueTrackListModel.removeRow(chosen.row())
        self.meta_info(location, active=True)
        self.play_track()

    def choose_track_from_recent(self, chosen):
        self.player.stop_item()
        location = chosen.data(1)
        self.recentTrackListModel.removeRow(chosen.row())
        if self.player.get_item() is not None:
            self.current_to_recent()
        self.player.set_item(location)
        self.play_track()
        self.meta_info(location, active=True)

    @pyqtSlot()
    def play_track(self):
        if self.player.get_item() is not None:
            self.player.play_item()
            self.video_window()
            print(self.player.status)
            if self.player.status == "paused":
                self.ui.playpauseButton.setIcon(self.play_icon)
            elif self.player.status == "playing":
                self.ui.playpauseButton.setIcon(self.pause_icon)
        else:
            print("No track to play")

    @pyqtSlot()
    def stop_track(self):
        if self.player.get_item() is not None:
            self.player.stop_item()
            print(self.player.status)
            self.ui.playpauseButton.setIcon(self.play_icon)

    @pyqtSlot()
    def next_track(self):
        error = "There's no track"
        try:
            self.current_to_recent()
            self.get_next_track()
            self.play_track()
        except AttributeError:
            print(error + " (" + AttributeError.__name__ + ")")
        except TypeError:
            print(error + " (" + TypeError.__name__ + ")")

    @pyqtSlot()
    def prev_track(self):
        previous_track = self.recentTrackListModel.takeItem(0)
        if previous_track is not None or previous_track is not "":
            try:
                location = previous_track.data(1)
                try:
                    self.player.stop_item()
                    print(self.player.get_item())
                    playing_track = self.player.get_item()
                    playing_meta = self.meta_info(playing_track)
                    item = QStandardItem(playing_track)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)  # This is necessary to drag'n'drop within QueueList
                    item.setText(playing_meta)
                    item.setData(playing_track, 1)
                    self.queueTrackListModel.insertRow(0, item)
                    print("goes back one step..")
                except FileNotFoundError:
                    print("no current track..")
                self.player.set_item(location)
                print("loaded: " + self.player.get_item())
                self.meta_info(location, active=True)
                self.recentTrackListModel.removeRow(0)
                print(previous_track.data(0) + " taken back from recent.")
                self.play_track()
            except AttributeError:
                print("nope")
        elif previous_track is None or previous_track is "":
            print("there's no track - cannot go backwards")

    def current_to_recent(self):
        track = self.player.get_item()
        if track is not "":
            item = QStandardItem(track)
            track_meta = self.meta_info(track)
            item.setText(track_meta)
            item.setData(track, 1)
            self.recentTrackListModel.insertRow(0, item)

    @pyqtSlot()
    def choose_track(self, arg=False):
        if arg is not False:
            chosen = [arg]
        elif arg is False:
            chosen = QFileDialog.getOpenFileName(parent=self.window, filter="Media (*.mp3 *.ogg *.oga *.wav *.flac *.wma *.mkv *.mp4 *.avi *.mpg *.ogv)", directory=os.getenv('HOME'))
        if chosen[0] != "":
            if self.player.status != "stopped":
                self.player.stop_item()
            if self.player.get_item() is not None:
                self.current_to_recent()
            location = chosen[0]
            self.player.set_item(location)
            print("loaded: " + self.player.get_item())
            self.meta_info(location, active=True)
            self.play_track()

    @pyqtSlot()
    def choose_tracks(self):
        chosen = QFileDialog.getOpenFileNames(parent=self.window, filter="Media (*.mp3 *.ogg *.oga *.wav *.flac *.wma *.mkv *.mp4 *.avi *.mpg *.ogv)", directory=os.getenv('HOME'))
        c = 0
        start_all = time.time()
        for track in chosen[c]:
            is_video = False
            for v in video_files:
                if track.lower().endswith(v):
                    is_video = True
            # Avoid threading when adding videos
            if is_video:
                self.process_track(track)
            else:
                queue.put(track)
            c += 1
        self.start_working(start_all, c)

    @pyqtSlot()
    def choose_directory(self, arg=False):
        if arg is not False:
            directory = [arg][0]
            dir_files = os.listdir(directory)
        else:
            directory = QFileDialog.getExistingDirectory(directory=os.getenv('HOME'))
            dir_files = os.listdir(directory)
        c = 0
        start_all = time.time()
        for track in dir_files:
            is_track = False
            is_video = False
            for a in audio_files:
                if track.lower().endswith(a):
                    is_track = True
            for v in video_files:
                if track.lower().endswith(v):
                    is_video = True
            if is_track:
                fullpath = os.path.realpath(directory) + "/" + track
                queue.put(fullpath)
                c += 1
            #Avoid threading in case of video
            if is_video is True:
                fullpath = os.path.realpath(directory) + "/" + track
                self.process_track(fullpath)
                c += 1
        self.start_working(start_all, c)

    def get_next_track(self):
        try:
            next_track = self.queueTrackListModel.takeItem(0)
            print("takes next track from queue..")
            location = next_track.data(1)
            self.player.set_item(location)
            print("loaded: " + self.player.get_item())
            self.meta_info(location, active=True)
            self.queueTrackListModel.removeRow(0)
            print(next_track.data(0) + " removed from queue.")
            self.play_track()
            self.ui.playpauseButton.setIcon(self.pause_icon)
        except AttributeError:
            print("queue's empty.. I'll hang back for now")
            self.player.reset()
            self.ui.playpauseButton.setIcon(self.play_icon)

    def meta_info(self, location, active=False):
        taginfo = os.path.basename(location)
        try:
            tagger = read_tag(location)
            taginfo = tagger.artist + " - " + tagger.title + " (" + tagger.album + ")"# + " (" + tagger.date + ")"
            if active is True:
                if len(taginfo) > 54:
                    taginfo = taginfo[:52]
                    self.ui.TrackInformationText.setText(taginfo + "..")
                else:
                    self.ui.TrackInformationText.setText(taginfo)
        except NameError:  # If NoTagError couldn't import because of lack of stagger
            if active is True:
                self.ui.TrackInformationText.setText(os.path.basename(location))
        except NoTagError:
            if active is True:
                self.ui.TrackInformationText.setText(os.path.basename(location))
        return taginfo

    def track_elapsed(self):
        track = self.player.track_item_pos()
        if self.player.status is "playing":
            # Song finished
            if track[3] >= track[4]:
                if track[4] != 0:  # test-fix for early track switching | booo
                    print("finished playing song")
                    self.current_to_recent()
                    self.player.stop_item()
                    self.get_next_track()
            # -||- but placeholder fix for 1sec left bug
            if track[3] == track[4] - 1:
                stuck = self.is_it()
                if stuck is True:
                    print("finished playing song (IN AN UGLY WAY)")
                    self.current_to_recent()
                    self.player.stop_item()
                    self.get_next_track()
            if track[4] != 0:
                self.ui.TrackElapsedText.setText("+" + track[0])
                self.ui.TrackLengthText.setText(track[1])
                self.ui.TrackLeftText.setText("-" + track[2])
                self.ui.TrackSlider.setMaximum(track[4])
                if self.player.status is not "paused":
                    self.ui.TrackSlider.setValue(track[3])

    def is_it(self):
            self.stuck_counter += 1
            if self.stuck_counter == 3:
                self.stuck_counter = 0
                return True
            else:
                return False

    def about_dialog(self):
        from PyQt5.QtWidgets import QDialog, QLabel, QWidget
        from PyQt5.QtCore import QRect

        d = QDialog(self.window)
        d.setWindowTitle("About LiMu")
        container = QWidget(d)
        container.setGeometry(QRect(0, 0, 200, 80))
        intro = QLabel(container)
        intro.setText("the Liothe Music Player")
        made_by = QLabel(container)
        made_by.setText("\nCreated by: Liothe")
        version = QLabel(container)
        version.setText("\n\nVersion: " + self.version)
        d.show()

    def process_track(self, track):
        with lock:
            start_single = time.time()
            item = QStandardItem(track)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)  # This is necessary to drag'n'drop within QueueList
            track_info = self.meta_info(track)
            item.setText(track_info)
            item.setData(track, 1)
            self.queueTrackListModel.appendRow(item)
            stop_single = time.time() - start_single
            print("queued:", os.path.basename(item.data(0)), "(" + str(stop_single.__round__(5)) + ")" + " --- " + threading.current_thread().name)
            if self.player.status is None:
                self.get_next_track()

    def start_working(self, start_time, count):
        for i in range(os.cpu_count()):
            threading.Thread(target=self.workerbee_do, daemon=True, name="workerbee " + str(i + 1)).start()
        stop_all = time.time() - start_time
        queue.join()
        with lock:
            print("Adding", str(count), "tracks took", str(stop_all.__round__(5)) + "seconds")

    def workerbee_do(self):
        while True:
            item = queue.get()
            self.process_track(item)
            queue.task_done()