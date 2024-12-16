#!/usr/bin/env python

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

gi.require_version("Gio", "2.0")
from gi.repository import Gio

import my_calendar

import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, message="Your system is avx2 capable but pygame was not built with support for it.")
import pygame


class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(300, 200)

        # Create a button
        button = Gtk.Button.new_with_label("Send Notification")
        button.connect("clicked", self.on_button_clicked)

        # Create a vertical box container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.append(button)

        self.set_child(vbox)

    def on_button_clicked(self, button):
        # Create a notification
        notification = Gio.Notification.new("Hello!")
        notification.set_body("Hello from GTK4!")
        notification.set_priority(Gio.NotificationPriority.NORMAL)

        # Send the notification
        self.get_application().send_notification("notification", notification)

        # Play a sound
        pygame.mixer.init()
        pygame.mixer.music.load("/usr/share/sounds/alsa/Front_Center.wav")
        pygame.mixer.music.play()

class MyApp(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_activate(self):
        window = MyWindow(application=self)
        window.present()

if __name__ == "__main__":
    ###app = MyApp(application_id="com.github.jhutar.meetings_notifier")
    ###app.run()
    cal = my_calendar.MyCalendar()
    print(cal.get_closest_meeting())
