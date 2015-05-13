__author__ = 'liothe'
import time
import os
from multiprocessing import Pool
from PyQt5 import QtWidgets, QtGui, QtCore
# Optional, for Track information
try:
    from stagger import read_tag, NoTagError, FrameWarning, EmptyFrameWarning
except ImportError:
    print("stagger wasn't found. (https://code.google.com/p/stagger/)")
    print("Unable to gather track information from mp3 files'.")


def get_meta_info(i, location, playing=False):
    taginfo = os.path.basename(location[0])
    try:
        tagger = read_tag(location[0])
        taginfo = tagger.artist + " - " + tagger.title + " (" + tagger.album + ")"# + " (" + tagger.date + ")"
        if playing is True:
            if len(taginfo) > 54:
                taginfo = taginfo[:52]
                i.TrackInformationText.setText(taginfo + "..")
            else:
                i.TrackInformationText.setText(taginfo)
    except NameError:  # If NoTagError couldn't import because of lack of stagger
        i.TrackInformationText.setText(os.path.basename(location[0]))
    except NoTagError:
        i.TrackInformationText.setText(os.path.basename(location[0]))
    #except EmptyFrameWarning:
    #    i.TrackInformationText.setText(os.path.basename(location[0]))
    #except FrameWarning:
    #    i.TrackInformationText.setText(os.path.basename(location[0]))
    return taginfo


def choose_from_queue(i, ThePlayer, recentList, queue):
    if ThePlayer.status is not "stopped":
        ThePlayer.stop_item()
    if ThePlayer.get_item() is not None:
        current_to_recent(i, ThePlayer.get_item(), recentList)
    ThePlayer.set_item(queue.data(1))
    print("loaded: " + ThePlayer.get_item())
    location = [queue.data(1)]
    queue.model().removeRow(queue.row())
    get_meta_info(i, location, playing=True)
    ThePlayer.play_item()


def choose_from_recent(i, ThePlayer, recentList, recent):
    if ThePlayer.status is not "stopped":
        ThePlayer.stop_item()
    was_playing = False
    if ThePlayer.get_item() is not None:
        old_track = ThePlayer.get_item()
        was_playing = True
    ThePlayer.set_item(recent.data(1))
    #  print("loaded: " + ThePlayer.get_item())
    location = [recent.data(1)]
    recent.model().removeRow(recent.row())
    get_meta_info(i, location, playing=True)
    ThePlayer.play_item()
    if was_playing is True:
        current_to_recent(i, old_track, recentList)


def choose_single(parent, i, ThePlayer, recent_list_model):
    chosen = QtWidgets.QFileDialog.getOpenFileName(parent=parent, filter="Media (*.mp3 *.ogg *.oga *.wav *.flac *.wma *.mkv *.mp4 *.avi *.mpg *.ogv)", directory=os.getenv('HOME'))
    if chosen[0] is not "":
        if ThePlayer.status != "stopped":
            ThePlayer.stop_item()
        if ThePlayer.get_item() is not None:
            current_to_recent(i, ThePlayer.get_item(), recent_list_model)
        ThePlayer.set_item(chosen[0])
        print("loaded: " + ThePlayer.get_item())
        location = chosen
        get_meta_info(i, location, playing=True)
        ThePlayer.play_item()


def add_queue(track, i, ThePlayer, list_model, printit, pause_icon):
    start = time.time()
    item = QtGui.QStandardItem(track)
    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsDropEnabled)  # This is necessary to drag'n'drop within QueueList
    track_info = get_meta_info(i, [track])
    item.setText(track_info)
    item.setData(track, 1)
    list_model.appendRow(item)
    stop = time.time() - start
    if printit is True:
        print("queued:", os.path.basename(item.data(0)), "(" + str(stop.__round__(5)) + ")")
    if ThePlayer.status is None:
        get_next(i, ThePlayer, list_model, pause_icon)


def choose_several(parent, i, ThePlayer, list_model, pause_icon):
    chosen = QtWidgets.QFileDialog.getOpenFileNames(parent=parent, filter="Media (*.mp3 *.ogg *.oga *.wav *.flac *.wma *.mkv *.mp4 *.avi *.mpg *.ogv)", directory=os.getenv('HOME'))
    show_terminal = True
    if len(chosen[0]) > 50:
        show_terminal = False
    c = 0
    start = time.time()
    for n in chosen[c]:
        add_queue(n, i, ThePlayer, list_model, show_terminal, pause_icon)
        c += 1
    stop = time.time() - start
    print("Adding", str(c), "tracks took", str(stop.__round__(5)) + "seconds")


def get_next(i, ThePlayer, list_model, pause_icon):
    try:
        next_track = list_model.takeItem(0)
        print("takes next track from queue..")
        ThePlayer.set_item(next_track.data(1))
        print("loaded: " + ThePlayer.get_item())
        list_model.removeRow(0)
        print(next_track.data(0) + " removed from queue.")
        get_meta_info(i, [next_track.data(1)], playing=True)
        ThePlayer.play_item()
        print(ThePlayer.get_item())
        if ThePlayer.status is "playing":
            i.playpauseButton.setIcon(pause_icon)
    except AttributeError:
        print("queue's empty.. I'll hang back for now")
        ThePlayer.reset()


def current_to_recent(i, track, list_model_for_recent):
    item = QtGui.QStandardItem(track)
    item.setText(get_meta_info(i, [track]))
    item.setData(track, 1)
    list_model_for_recent.insertRow(0, item)


def elapsed(i, ThePlayer, list_model, list_model_for_recent, pause_icon):
    track = ThePlayer.track_item_pos()
    if ThePlayer.status is "playing":
        if track[3] >= track[4]:
            print("finished playing song")
            current_to_recent(i, ThePlayer.get_item(), list_model_for_recent)
            ThePlayer.stop_item()
            get_next(i, ThePlayer, list_model, pause_icon)
        if track[3] == track[4] - 1:  # Placeholder fix for 1sec left bug
            stuck = is_it()
            if stuck is True:
                print("finished playing song (IN AN UGLY WAY)")
                current_to_recent(i, ThePlayer.get_item(), list_model_for_recent)
                ThePlayer.stop_item()
                get_next(i, ThePlayer, list_model, pause_icon)
        if track[4] != 0:
            i.TrackElapsedText.setText("+" + track[0])
            i.TrackLengthText.setText(track[1])
            i.TrackLeftText.setText("-" + track[2])
            i.TrackSlider.setMaximum(track[4])
            if ThePlayer.status is not "paused":
                i.TrackSlider.setValue(track[3])


stuck_counter = 0
def is_it():
    global stuck_counter
    stuck_counter += 1
    if stuck_counter == 3:
        stuck_counter = 0
        return True
    else:
        return False