#!/usr/bin/env python3

# Original code (C) Aleksander Alekseev 2016, http://eax.me/

import signal
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gi.repository import GObject

gi.require_version("Notify", "0.7")
from gi.repository import Notify

from . import my_calendar
from . import my_sound


APPID = "com.github.jhutar.meetings-notifier"
CURRDIR = os.path.dirname(os.path.abspath(__file__))
ICON = os.path.join(CURRDIR, "python3.xpm")


class MyHandler:

    def __init__(self, builder, calendar):
        self.calendar = calendar

        self.builder = builder
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("window1")
        self.window.set_icon_from_file(ICON)
        self.window.hide()
        self.window_is_hidden = True

        self.menu = builder.get_object("menu1")
        self.trayicon = Gtk.StatusIcon()
        self.trayicon.set_from_file(ICON)
        self.trayicon.connect("popup-menu", self.onPopupMenu)
        self.trayicon.connect("activate", self.onShowOrHide)

        text_view = self.builder.get_object("text1")
        self.buffer = text_view.get_buffer()

        self.onTextChange()

    def onPopupMenu(self, icon, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

    def onNotify(self, *args):
        Notify.Notification.new("Notification", str(self.calendar.get_closest_meeting()), ICON).show()
        my_sound.play()

    def onShowOrHide(self, *args):
        if self.window_is_hidden:
            self.window.show()
            self.window_is_hidden = False
        else:
            self.window.hide()
            self.window_is_hidden = True

    def onTextChange(self):
        text = str(self.calendar.get_closest_meeting())
        self.buffer.set_text(text)
        GObject.timeout_add_seconds(3, self.onTextChange) 

    def onQuit(self, *args):
        Notify.uninit()
        Gtk.main_quit()


def main():
    # Handle pressing Ctr+C properly, ignored by default
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    calendar = my_calendar.MyCalendar()

    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(CURRDIR, "meetings_notifier.glade"))

    handler = MyHandler(builder, calendar)

    print(calendar.get_closest_meeting())

    Notify.init(APPID)

    Gtk.main()
