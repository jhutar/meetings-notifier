#!/usr/bin/env python

import unittest
from unittest.mock import Mock, patch

from .context import meetings_notifier


class TestCalendar(unittest.TestCase):
    def test_get_data(self):
        mocked_calendar = Mock()   # Calendar is not called, so we do not specify return_value
        #mocked_calendar.events = Mock()   # This is default
        #mocked_calendar.events.return_value = Mock()   # This allows calendar.events()
        #mocked_calendar.events.return_value.list = Mock()   # Again, default
        #mocked_calendar.events.return_value.list.return_value = Mock()   # Allowd calendar.events().list()
        #mocked_calendar.events.return_value.list.return_value.execute = Mock()   # Default, not needed
        mocked_calendar.events.return_value.list.return_value.execute.return_value = {"items": []}   # This allows calendar.events().list().execute()
        def mocked_refresh_credentials(self):
            self.calendar = mocked_calendar

        with patch.object(meetings_notifier.my_calendar.MyCalendar, '_refresh_credentials', mocked_refresh_credentials) as mock_populate:
            calendar = meetings_notifier.my_calendar.MyCalendar()
