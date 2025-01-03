#!/usr/bin/env python3

# Original code (C) Aleksander Alekseev 2016, http://eax.me/

import datetime
import logging
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
TIMER_CALENDAR_REFRESH = 60
TIMER_WINDOW_TEXT_REFRESH = 3
TIMER_ALERT_CHECK = 3
ALERT_URGENCY_1_AFTER = 100
#ALERT_URGENCY_1_AFTER = (datetime.datetime.fromisoformat("2025-01-03T07:00:00+00:00") - datetime.datetime.now(datetime.timezone.utc)).seconds - 2
ALERT_URGENCY_2_AFTER = 30
ALERT_URGENCY_3_AFTER = 10
ALERT_IGNORE_AFTER = -600


def event_to_text(event):
    if event == {}:
        return "No event"
    else:
        return f"When: {event['start']['dateTime'].isoformat()}\nWhat: {event['summary']}\n"


def event_to_log(event):
    if event == {}:
        return "No event"
    else:
        return f"{event['summary']}/{event['id']}({event['start']['dateTime'].isoformat()})"


class MyHandler:

    STATUS_WAITING = 0
    STATUS_URGENCY_1 = 1
    STATUS_ACKNOWLEADGED = 10

    def __init__(self, builder, calendar):
        self.status = {}

        self.calendar = calendar
        GObject.timeout_add_seconds(TIMER_CALENDAR_REFRESH, self.calendar.refresh_events)

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
        GObject.timeout_add_seconds(TIMER_WINDOW_TEXT_REFRESH, self.onTextChange)
        self.onTextChange()

        GObject.timeout_add_seconds(TIMER_WINDOW_TEXT_REFRESH, self.onAlertCheck)

    def onPopupMenu(self, icon, button, time):
        self.menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)

    def onNotify(self, *args):
        event = self.calendar.get_closest_meeting()
        event_id = event["id"]
        text = event_to_text(event)
        notification = Notify.Notification.new("Notification", text, ICON)
        notification.set_urgency(Notify.Urgency.CRITICAL)
        notification.add_action("acknowleadge", "Acknowleadge", self.onAlertAcknowleadge)
        notification.show()
        notification.event_id = event_id   # HACK: Pass event ID with notification - it is used by acknowleadge callback
        self.status[event_id]["notification"] = notification

    def onShowOrHide(self, *args):
        if self.window_is_hidden:
            self.window.show()
            self.window_is_hidden = False
        else:
            self.window.hide()
            self.window_is_hidden = True

    def onTextChange(self):
        text = ""
        for event in self.calendar.events:
            text += event_to_text(event) + "\n"
        self.buffer.set_text(text)
        return True

    def onAlertCheck(self):
        event = self.calendar.get_closest_meeting()
        if event == {}:
            return

        event_id = event["id"]
        if event_id not in self.status:
            self.status[event_id] = {"status": self.STATUS_WAITING}

        now = datetime.datetime.now(datetime.timezone.utc)
        event_in = (event["start"]["dateTime"] - now).seconds
        if event_in < ALERT_IGNORE_AFTER:
            logging.warning(f"Ignoring event {event_to_log(event)} as it is overdue: {event_in}")
        elif event_in < ALERT_URGENCY_3_AFTER:
            logging.info(f"Event {event_to_log(event)} almost starts: {event_in}")
            if self.status[event_id]["status"] < self.STATUS_URGENCY_3:
                self.status[event_id]["status"] = self.STATUS_URGENCY_3
                self.onNotify()
                my_sound.play()
        elif event_in < ALERT_URGENCY_2_AFTER:
            logging.info(f"Event {event_to_log(event)} starts in a bit: {event_in}")
            if self.status[event_id]["status"] < self.STATUS_URGENCY_2:
                self.status[event_id]["status"] = self.STATUS_URGENCY_2
                self.onNotify()
        elif event_in < ALERT_URGENCY_1_AFTER:
            logging.info(f"Event {event_to_log(event)} soon to start: {event_in}")
            if self.status[event_id]["status"] < self.STATUS_URGENCY_1:
                self.status[event_id]["status"] = self.STATUS_URGENCY_1
                self.onNotify()
        else:
            pass

        return True

    def onAlertAcknowleadge(self, notification, action):
        if action == "acknowleadge":
            self.status[notification.event_id]["status"] = self.STATUS_ACKNOWLEADGED

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

    Notify.init(APPID)

    Gtk.main()
