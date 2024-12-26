#!/usr/bin/env python3

# Original code (C) Aleksander Alekseev 2016, http://eax.me/

import signal
import os
import gi

import warnings

warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message="Your system is avx2 capable but pygame was not built with support for it.",
)
import pygame

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

gi.require_version("Notify", "0.7")
from gi.repository import Notify

import my_calendar


APPID = "com.github.jhutar.meetings-notifier"
CURRDIR = os.path.dirname(os.path.abspath(__file__))
ICON = os.path.join(CURRDIR, "python3.xpm")


class MyStatusIcon:

    def __init__(self, appid, icon, menu):
        self.menu = menu

        self.ind = Gtk.StatusIcon()
        self.ind.set_from_file(icon)
        self.ind.connect("popup-menu", self.onPopupMenu)

    def onPopupMenu(self, icon, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)


class MyHandler:

    def __init__(self, calendar):
        self.calendar = calendar

        self.window_is_hidden = True

    def onNotify(self, *args):
        Notify.Notification.new("Notification", str(self.calendar.get_closest_meeting()), ICON).show()

        # Play a sound
        pygame.mixer.init()
        pygame.mixer.music.load("/usr/share/sounds/alsa/Front_Center.wav")
        pygame.mixer.music.play()

    def onShowOrHide(self, *args):
        if self.window_is_hidden:
            window.show()
        else:
            window.hide()

        self.window_is_hidden = not self.window_is_hidden

    def onQuit(self, *args):
        Notify.uninit()
        Gtk.main_quit()


# Handle pressing Ctr+C properly, ignored by default
signal.signal(signal.SIGINT, signal.SIG_DFL)

calendar = my_calendar.MyCalendar()
sys.exit()

handler = MyHandler(calendar)

builder = Gtk.Builder()
builder.add_from_file("meetings_notifier.glade")
builder.connect_signals(handler)

window = builder.get_object("window1")
window.set_icon_from_file(ICON)
window.hide()
handler.window_is_hidden = True

menu = builder.get_object("menu1")
icon = MyStatusIcon(APPID, ICON, menu)

print(calendar.get_closest_meeting())

Notify.init(APPID)

Gtk.main()
