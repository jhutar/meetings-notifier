#!/usr/bin/env python3

# Original code (C) Aleksander Alekseev 2016, http://eax.me/

import signal
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

gi.require_version("Notify", "0.7")
from gi.repository import Notify

from . import my_calendar
from . import my_sound


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

        self.window = None
        self.window_is_hidden = True

    def onNotify(self, *args):
        Notify.Notification.new("Notification", str(self.calendar.get_closest_meeting()), ICON).show()

        # Play a sound
        my_sound.play()

    def onShowOrHide(self, *args):
        if self.window_is_hidden:
            self.window.show()
        else:
            self.window.hide()

        self.window_is_hidden = not self.window_is_hidden

    def onQuit(self, *args):
        Notify.uninit()
        Gtk.main_quit()


def main():
    # Handle pressing Ctr+C properly, ignored by default
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    calendar = my_calendar.MyCalendar()
    ###print(calendar.get_closest_meeting())
    ###import sys
    ###sys.exit()

    handler = MyHandler(calendar)

    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(CURRDIR, "meetings_notifier.glade"))
    builder.connect_signals(handler)

    window = builder.get_object("window1")
    window.set_icon_from_file(ICON)
    window.hide()
    handler.window = window
    handler.window_is_hidden = True

    menu = builder.get_object("menu1")
    icon = MyStatusIcon(APPID, ICON, menu)

    print(calendar.get_closest_meeting())

    Notify.init(APPID)

    Gtk.main()
