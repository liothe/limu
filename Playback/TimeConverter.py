__author__ = 'liothe'

from datetime import datetime, timedelta


def convert(number):
    number_delta = timedelta(seconds=number)
    d = datetime(2000, 1, 1) + number_delta

    result = format_numbers(d.second, d.minute, d.hour)
    return result


def calculate_time_left(position, duration):
    left = duration - position
    left = timedelta(seconds=left)
    d = datetime(2000, 1, 1) + left

    time_left = format_numbers(d.second, d.minute, d.hour)
    return time_left


def format_numbers(s, m, h):
    if s < 10:
        second = "0%d" % s
    else:
        second = "%d" % s

    if m < 10:
        minute = "0%d:" % m
    else:
        minute = "%d:" % m

    if h < 10:
        hour = "0%d:" % h
    else:
        hour = "%d:" % h

    if h == 0:
        hour = ""
        if m == 0:
            minute = ""
            if s < 10:
                second = "%d" % s

    return hour + minute + second