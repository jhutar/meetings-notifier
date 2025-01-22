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


APPID = "com.github.jhutar.meetings-notifier"
CURRDIR = os.path.dirname(os.path.abspath(__file__))
ICON = os.path.join(CURRDIR, "python3.xpm")
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


class MyHandler:

    def __init__(self, calendar):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = helpers.MyConfig()

        self.sound = my_sound.MySound(self.config.config)

        self.calendar = calendar
        GObject.timeout_add_seconds(TIMER_CALENDAR_REFRESH, self.calendar.refresh_events)

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(CURRDIR, "meetings_notifier.glade"))
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("window1")
        self.window.set_icon_from_file(ICON)
        self.window.hide()
        self.window_is_hidden = True

        self.menu = self.builder.get_object("menu1")
        self.trayicon = Gtk.StatusIcon()
        self.trayicon.set_from_file(ICON)
        self.trayicon.connect("popup-menu", self.onPopupMenu)
        self.trayicon.connect("activate", self.onShowOrHide)

        text_view = self.builder.get_object("text1")
        self.buffer = text_view.get_buffer()
        GObject.timeout_add_seconds(TIMER_WINDOW_TEXT_REFRESH, self.onTextChange)
        self.onTextChange()

        GObject.timeout_add_seconds(TIMER_WINDOW_TEXT_REFRESH, self.onAlertCheck)

    def run(self):
        Notify.init(APPID)
        return Gtk.main()

    def onPopupMenu(self, icon, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

    def onNotify(self, event_id):
        text = helpers.event_to_text(self.calendar.events[event_id])
        notification = Notify.Notification.new("Notification", text, ICON)
        notification.set_urgency(Notify.Urgency.CRITICAL)
        notification.add_action("acknowleadge", "Acknowleadge", self.onAlertAcknowleadge)
        notification.show()
        notification.event_id = event_id   # HACK: Pass event ID with notification - it is used by acknowleadge callback
        self.calendar.set_notification(event_id, notification)

    def onShowOrHide(self, *args):
        if self.window_is_hidden:
            self.window.show()
            self.window_is_hidden = False
        else:
            self.window.hide()
            self.window_is_hidden = True

    def onTextChange(self):
        text = ""
        for event in self.calendar.events.values():
            text += helpers.event_to_text(event) + "\n"
        self.buffer.set_text(text)
        return True

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

    def onAlertAcknowleadge(self, notification, action):
        if action == "acknowleadge":
            if self.calendar.set_status(notification.event_id, my_calendar.STATUS_ACKNOWLEADGED):
                self.logger.info(f"Event {notification.event_id} was acknowleadged")

    def onQuit(self, *args):
        Notify.uninit()
        Gtk.main_quit()
