#!/usr/bin/env python3

# Original code (C) Aleksander Alekseev 2016, http://eax.me/

import datetime
import logging
import os
import yaml
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gi.repository import GObject

gi.require_version("Notify", "0.7")
from gi.repository import Notify

from . import my_calendar
from . import my_sound
from . import helpers


ICON = os.path.join(helpers.CURRDIR, "resources/python.xpm")
TIMER_CALENDAR_REFRESH = 60
TIMER_WINDOW_TEXT_REFRESH = 3
TIMER_ALERT_CHECK = 3
ALERT_URGENCY_1_AFTER = 100
ALERT_URGENCY_2_AFTER = 30
ALERT_URGENCY_3_AFTER = 10
ALERT_URGENCY_3_AFTER = (datetime.datetime.fromisoformat("2025-01-09T17:30:00+00:00") - datetime.datetime.now(datetime.timezone.utc)).seconds - 2
ALERT_IGNORE_AFTER = -600


class MyAlerter:
    def __init__(self, calendar):
        self.calendar = calendar
        self.logger = logging.getLogger(self.__class__.__name__)

        self.do_notify = False
        self.do_icon = False
        self.do_sound = False

        self.notify_thread = threading.Thread(target=self.notify_thread_func)
        self.icon_thread = threading.Thread(target=self.icon_thread_func)
        self.sound_thread = threading.Thread(target=self.sound_thread_func)

        self.notify_thread.start()
        self.icon_thread.start()
        self.sound_thread.start()

    def notify_thread_func(self):
        while True:
            if self.do_notify:
                print("Hello (Notify)")
            time.sleep(10)

    def icon_thread_func(self):
        while True:
            if self.do_icon:
                print("Hello (Icon)")
            time.sleep(10)

    def sound_thread_func(self):
        while True:
            if self.do_sound:
                print("Hello (Sound)")
            time.sleep(10)


class MyMenu:

    def __init__(self, builder):
        self._menu = builder.get_object("menu1")

    def popup(self, icon, button, time):
        self._menu.popup(
            None,
            None,
            Gtk.StatusIcon.position_menu,
            icon,
            button,
            time,
        )


class MyIcon:

    def __init__(self, menu_popup_callback, window_toggle_callback):
        self._menu_popup_callback = menu_popup_callback
        self._window_toggle_callback = window_toggle_callback

        self._trayicon = Gtk.StatusIcon()
        self._trayicon.set_from_file(ICON)
        self._trayicon.connect("popup-menu", self.popup_menu)
        self._trayicon.connect("activate", self.toggle_window)

    def popup_menu(self, *args):
        self._menu_popup_callback(*args)

    def toggle_window(self, *args):
        self._window_toggle_callback()


class MyWindow:

    def __init__(self, builder, calendar):
        self._calendar = calendar

        builder.connect_signals(self)

        self._window = builder.get_object("window1")
        self._window.set_icon_from_file(ICON)
        self._window.hide()
        self._window_is_hidden = True

        text_view = builder.get_object("text1")
        self._buffer = text_view.get_buffer()
        GObject.timeout_add_seconds(TIMER_WINDOW_TEXT_REFRESH, self.refresh_text)
        self.refresh_text()

    def refresh_text(self):
        text = ""
        for event in self._calendar.events.values():
            text += helpers.event_to_text(event) + "\n"
        self._buffer.set_text(text)
        return True   # makes sure timer will not stop

    def toggle(self, *args):
        if self._window_is_hidden:
            self._window.show()
            self._window_is_hidden = False
        else:
            self._window.hide()
            self._window_is_hidden = True

    def quit(self, *args):
        Notify.uninit()
        Gtk.main_quit()


class MyNotification:

    def __init__(self):
        Notify.init(helpers.APP_ID)

    def show(self, event_id):
        text = helpers.event_to_text(self.calendar.events[event_id])
        notification = Notify.Notification.new("Notification", text, ICON)
        notification.set_urgency(Notify.Urgency.CRITICAL)
        notification.add_action("acknowleadge", "Acknowleadge", self.acknowleadge)
        notification.show()
        self.event_id = event_id
        self.calendar.set_notification(event_id, notification)

    def acknowleadge(self, notification, action):
        if action == "acknowleadge":
            if self.calendar.set_status(self.event_id, my_calendar.STATUS_ACKNOWLEADGED):
                self.logger.info(f"Event {self.event_id} was acknowleadged")




class MyHandler:

    def __init__(self, calendar):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = helpers.MyConfig()

        self.sound = my_sound.MySound(self.config.config)

        self.calendar = calendar
        GObject.timeout_add_seconds(TIMER_CALENDAR_REFRESH, self.calendar.refresh_events)

        glade_file = os.path.join(
            helpers.CURRDIR,
            f"resources/{helpers.APP_NAME}.glade",
        )
        self._builder = Gtk.Builder()
        self._builder.add_from_file(glade_file)

        self._window = MyWindow(self._builder, calendar)
        self._menu = MyMenu(self._builder)
        self._icon = MyIcon(self._menu.popup, self._window.toggle)

        GObject.timeout_add_seconds(TIMER_WINDOW_TEXT_REFRESH, self.onAlertCheck)

    def run(self):
        return Gtk.main()

    def onAlertCheck(self):
        for event_id, event in self.calendar.events.items():
            if self.calendar.get_status(event_id) >= my_calendar.STATUS_ACKNOWLEADGED:
                continue

            now = datetime.datetime.now(datetime.timezone.utc)
            event_in = (event["start"] - now).total_seconds()

            if event_in < ALERT_IGNORE_AFTER:
                self.logger.warning(f"Ignoring event {helpers.event_to_log(event)} as it is overdue: {event_in}")
                self.calendar.set_status(event_id, my_calendar.STATUS_ACKNOWLEADGED)
                continue

            if event_in < ALERT_URGENCY_3_AFTER:
                if self.calendar.set_status(event_id, my_calendar.STATUS_URGENCY_3):
                    self.logger.info(f"Event {helpers.event_to_log(event)} almost starts: {event_in}")
                    self.onNotify(event_id)
                    self.sound.play()
                    continue

            if event_in < ALERT_URGENCY_2_AFTER:
                if self.calendar.set_status(event_id, my_calendar.STATUS_URGENCY_2):
                    self.logger.info(f"Event {helpers.event_to_log(event)} starts in a bit: {event_in}")
                    self.onNotify(event_id)
                    continue

            if event_in < ALERT_URGENCY_1_AFTER:
                if self.calendar.set_status(event_id, my_calendar.STATUS_URGENCY_1):
                    self.logger.info(f"Event {helpers.event_to_log(event)} soon to start: {event_in}")
                    self.onNotify()
                    continue

        return True
