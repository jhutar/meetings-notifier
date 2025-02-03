#!/usr/bin/env python3

# Original code (C) Aleksander Alekseev 2016, http://eax.me/

import datetime
import logging
import os
import threading
import time
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
ALERT_URGENCY_1_AFTER = 200000
ALERT_URGENCY_2_AFTER = 30
ALERT_URGENCY_3_AFTER = 10
ALERT_IGNORE_AFTER = -600


class MyAlerter:
    def __init__(self, icon, sound):
        self.logger = logging.getLogger(self.__class__.__name__)

        self._notification = None
        self._icon = icon
        self._sound = sound
        self._event = None

        self.do_notify = False
        self.do_icon = False
        self.do_sound = False

        self.notify_thread = threading.Thread(target=self.notify_thread_func)
        self.icon_thread = threading.Thread(target=self.icon_thread_func)
        self.sound_thread = threading.Thread(target=self.sound_thread_func)

        self.notify_thread.start()
        self.icon_thread.start()
        self.sound_thread.start()

    def set_event(self, event, urgency):
        self._event = event
        if urgency == 1:
            self.do_notify, self.do_icon, self.do_sound = (True, False, False)
        elif urgency == 2:
            self.do_notify, self.do_icon, self.do_sound = (True, True, False)
        elif urgency == 3:
            self.do_notify, self.do_icon, self.do_sound = (True, True, True)
        else:
            self.logger.warning(f"Unknown urgency for event {event}: {urgency}")

    def reset_event(self):
        # If some notification is active, remove it
        if self._notification is not None:
            self._notification.close()

        self.do_notify, self.do_icon, self.do_sound = (False, False, False)
        self._event = None

    def ack_event(self):
        self._event.acknowleadged = True
        self.reset_event()

    def notify_thread_func(self):
        while True:
            if self.do_notify:
                print(f"Alerter notify {self._event}")
                if self._notification is not None:
                    self._notification.close()
                self._notification = MyNotification(self._event, self.ack_event)
            time.sleep(10)

    def icon_thread_func(self):
        while True:
            if self.do_icon:
                print(f"Alerter icon {self._event}")
            time.sleep(10)

    def sound_thread_func(self):
        while True:
            if self.do_sound:
                print(f"Alerter sound {self._event}")
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
        for event in self._calendar.events:
            text += event.to_text() + "\n"
        self._buffer.set_text(text)
        return True   # makes sure timer will not stop

    def toggle(self, *args):
        if self._window_is_hidden:
            self._window.show()
            self._window_is_hidden = False
        else:
            self._window.hide()
            self._window_is_hidden = True

    def run(self):
        Notify.init(helpers.APP_ID)
        return Gtk.main()

    def quit(self, *args):
        Notify.uninit()
        Gtk.main_quit()


class MyNotification:

    def __init__(self, event, ack_callback):
        self.logger = logging.getLogger(self.__class__.__name__)

        self._event = event
        self._ack_callback = ack_callback

        text = self._event.to_text()
        self._notification = Notify.Notification.new("Notification", text, ICON)
        self._notification.set_urgency(Notify.Urgency.CRITICAL)
        self._notification.set_timeout(10 * 1000)
        self._notification.add_action("acknowleadge", "Acknowleadge", self.acknowleadge)
        self._notification.show()

    def acknowleadge(self, notification, action):
        if action == "acknowleadge":
            self.logger.info(f"Event {self._event} acknowleadged")
            self._ack_callback()

    def close(self):
        self._notification.close()
        self._notification = None


class MyApplication:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = helpers.MyConfig()

        self._sound = my_sound.MySound(self.config.config)

        self.calendar = my_calendar.MyCalendar()
        GObject.timeout_add_seconds(TIMER_CALENDAR_REFRESH, self.calendar.refresh_events)

        glade_file = os.path.join(
            helpers.CURRDIR,
            f"resources/{helpers.APP_NAME}.glade",
        )
        self._builder = Gtk.Builder()
        self._builder.add_from_file(glade_file)

        self._window = MyWindow(self._builder, self.calendar)
        self._menu = MyMenu(self._builder)
        self._icon = MyIcon(self._menu.popup, self._window.toggle)

        self.alerter = MyAlerter(self._icon, self._sound)

        GObject.timeout_add_seconds(TIMER_WINDOW_TEXT_REFRESH, self.onAlertCheck)

    def run(self):
        return self._window.run()

    def _get_more_urgent(self, eu1, eu2):
        """Decide which touple of event and it's urgency is more important."""
        event1, urgency1 = eu1
        event2, urgency2 = eu2

        if event1 is None:
            return eu2

        if urgency1 == urgency2:
            if event1.start < event2.start:
                return eu1
            else:
                return eu2
        else:
            if urgency1 > urgency2:
                return eu1
            else:
                return eu2

    def onAlertCheck(self):
        alert = (None, 0)   # event and it's urgency with highest score

        for event in self.calendar.events:
            if event.acknowleadged:
                continue

            now = datetime.datetime.now(datetime.timezone.utc)
            event_in = (event.start - now).total_seconds()

            if event_in < ALERT_IGNORE_AFTER:
                self.logger.warning(f"Ignoring event {event} as it is overdue: {event_in}")
                event.acknowleadged = True
                continue

            if event_in < ALERT_URGENCY_3_AFTER:
                alert = self._get_more_urgent(alert, (event, 3))
                continue

            if event_in < ALERT_URGENCY_2_AFTER:
                alert = self._get_more_urgent(alert, (event, 2))
                continue

            if event_in < ALERT_URGENCY_1_AFTER:
                alert = self._get_more_urgent(alert, (event, 1))
                continue

        if alert[0] is not None:
            self.logger.debug(f"Event {alert[0]} soon to start, urgency {alert[1]}")
            self.alerter.set_event(*alert)

        return True
