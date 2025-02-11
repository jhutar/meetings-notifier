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


ICON_IDLE = os.path.join(helpers.CURRDIR, "resources/icon_idle.svg")
ICON_1 = os.path.join(helpers.CURRDIR, "resources/icon_1.svg")
ICON_2 = os.path.join(helpers.CURRDIR, "resources/icon_2.svg")
ICON_3 = os.path.join(helpers.CURRDIR, "resources/icon_3.svg")


class MyAlerter:
    def __init__(self, notify, icon, sound):
        self.logger = logging.getLogger(self.__class__.__name__)

        self._notify = notify
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
        self._notify.close()

        self.do_notify, self.do_icon, self.do_sound = (False, False, False)
        self._event = None

    def ack_event(self):
        self._event.acknowleadged = True
        self.reset_event()

    def notify_thread_func(self):
        while True:
            if self.do_notify:
                print(f"Alerter notify {self._event}")
                self._notify.close()
                self._notify.notify(self._event, self.ack_event)
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
                self._sound.play()
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
        self._trayicon.set_from_file(ICON_IDLE)
        self._trayicon.connect("popup-menu", self.popup_menu)
        self._trayicon.connect("activate", self.toggle_window)

    def popup_menu(self, *args):
        self._menu_popup_callback(*args)

    def toggle_window(self, *args):
        self._window_toggle_callback()


class MyWindow:

    def __init__(self, builder, calendar, config):
        self._calendar = calendar

        builder.connect_signals(self)

        self._window = builder.get_object("window1")
        self._window.set_icon_from_file(ICON_IDLE)
        self._window.hide()
        self._window_is_hidden = True

        text_view = builder.get_object("text1")
        self._buffer = text_view.get_buffer()
        GObject.timeout_add_seconds(
            config.config["timers"]["window_text"],
            self.refresh_text,
        )
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
        return Gtk.main()

    def quit(self, *args):
        Gtk.main_quit()


class MyNotification:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        Notify.init(helpers.APP_ID)

        self._event = None
        self._ack_callback = None
        self._notification = None

    def notify(self, event, ack_callback):
        self._event = event
        self._ack_callback = ack_callback

        text = self._event.to_text()
        self._notification = Notify.Notification.new("Notification", text, ICON_1)
        self._notification.set_urgency(Notify.Urgency.CRITICAL)
        self._notification.set_timeout(10 * 1000)
        self._notification.add_action("acknowleadge", "Acknowleadge", self.acknowleadge)
        self._notification.show()

    def acknowleadge(self, notification, action):
        if action == "acknowleadge":
            self.logger.info(f"Event {self._event} acknowleadged")
            self._ack_callback()

    def close(self):
        if self._notification is not None:
            self._notification.close()
            self._notification = None

    def quit(self):
        Notify.uninit()


class MyApplication:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.config = helpers.MyConfig()

        self.calendar = my_calendar.MyCalendar()
        GObject.timeout_add_seconds(
            self.config.config["timers"]["calendar_refresh"],
            self.calendar.refresh_events,
        )

        glade_file = os.path.join(
            helpers.CURRDIR,
            f"resources/{helpers.APP_NAME}.glade",
        )
        self._builder = Gtk.Builder()
        self._builder.add_from_file(glade_file)

        self._window = MyWindow(self._builder, self.calendar, self.config)
        self._menu = MyMenu(self._builder)
        self._icon = MyIcon(self._menu.popup, self._window.toggle)
        self._notify = MyNotification()
        self._sound = my_sound.MySound(self.config)

        self.alerter = MyAlerter(self._notify, self._icon, self._sound)

        GObject.timeout_add_seconds(
            self.config.config["timers"]["alert_check"],
            self.onAlertCheck,
        )

    def run(self):
        out = self._window.run()
        self._notify.quit()
        return out

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

            if event_in < self.config.config["alerts"]["ignore"]:
                self.logger.warning(f"Ignoring event {event} as it is overdue: {event_in}")
                event.acknowleadged = True
                continue

            if event_in < self.config.config["alerts"]["urgency_3"]:
                alert = self._get_more_urgent(alert, (event, 3))
                continue

            if event_in < self.config.config["alerts"]["urgency_2"]:
                alert = self._get_more_urgent(alert, (event, 2))
                continue

            if event_in < self.config.config["alerts"]["urgency_1"]:
                alert = self._get_more_urgent(alert, (event, 1))
                continue

        if alert[0] is not None:
            self.logger.debug(f"Event {alert[0]} soon to start, urgency {alert[1]}")
            self.alerter.set_event(*alert)

        return True
