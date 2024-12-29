#!/usr/bin/env python

import datetime
import unittest
from unittest.mock import Mock, patch

from .context import meetings_notifier

CAL_FIRST = {
    "kind": "calendar#events",
    "etag": '"p320bh1vclb5ok0o"',
    "summary": "Jan Hutar",
    "description": "",
    "updated": "2024-12-28T20:46:46.656Z",
    "timeZone": "Europe/Prague",
    "accessRole": "owner",
    "defaultReminders": [{"method": "email", "minutes": 1440}],
    "nextSyncToken": "CIC4h-yqy4oDEIC4h-yqy4oDGAUg092S0QIo092S0QI=",
    "items": [
        {
            "kind": "calendar#event",
            "etag": '"3469404706564000"',
            "id": "7eedg0m1svpv1v62720lse3k1j_20241229T160000Z",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=N2VlZGcwbTFzdnB2MXY2MjcyMGxzZTNrMWpfMjAyNDEyMjlUMTYwMDAwWiBqaHV0YXJAbQ&ctz=UTC",
            "created": "2024-12-20T13:45:53.000Z",
            "updated": "2024-12-20T13:45:53.282Z",
            "summary": "Test2",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@gmail.com", "self": True},
            "start": {"dateTime": "2024-12-29T16:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2024-12-29T17:00:00Z", "timeZone": "Europe/Prague"},
            "recurringEventId": "7eedg0m1svpv1v62720lse3k1j",
            "originalStartTime": {
                "dateTime": "2024-12-29T16:00:00Z",
                "timeZone": "Europe/Prague",
            },
            "iCalUID": "7eedg0m1svpv1v62720lse3k1j@google.com",
            "sequence": 0,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3469404706564000"',
            "id": "7eedg0m1svpv1v62720lse3k1j_20241230T160000Z",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=N2VlZGcwbTFzdnB2MXY2MjcyMGxzZTNrMWpfMjAyNDEyMzBUMTYwMDAwWiBqaHV0YXJAbQ&ctz=UTC",
            "created": "2024-12-20T13:45:53.000Z",
            "updated": "2024-12-20T13:45:53.282Z",
            "summary": "Test2",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@gmail.com", "self": True},
            "start": {"dateTime": "2024-12-30T16:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2024-12-30T17:00:00Z", "timeZone": "Europe/Prague"},
            "recurringEventId": "7eedg0m1svpv1v62720lse3k1j",
            "originalStartTime": {
                "dateTime": "2024-12-30T16:00:00Z",
                "timeZone": "Europe/Prague",
            },
            "iCalUID": "7eedg0m1svpv1v62720lse3k1j@google.com",
            "sequence": 0,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3469404706564000"',
            "id": "7eedg0m1svpv1v62720lse3k1j_20241231T160000Z",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=N2VlZGcwbTFzdnB2MXY2MjcyMGxzZTNrMWpfMjAyNDEyMzFUMTYwMDAwWiBqaHV0YXJAbQ&ctz=UTC",
            "created": "2024-12-20T13:45:53.000Z",
            "updated": "2024-12-20T13:45:53.282Z",
            "summary": "Test2",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@gmail.com", "self": True},
            "start": {"dateTime": "2024-12-31T16:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2024-12-31T17:00:00Z", "timeZone": "Europe/Prague"},
            "recurringEventId": "7eedg0m1svpv1v62720lse3k1j",
            "originalStartTime": {
                "dateTime": "2024-12-31T16:00:00Z",
                "timeZone": "Europe/Prague",
            },
            "iCalUID": "7eedg0m1svpv1v62720lse3k1j@google.com",
            "sequence": 0,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3469404706564000"',
            "id": "7eedg0m1svpv1v62720lse3k1j_20250101T160000Z",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=N2VlZGcwbTFzdnB2MXY2MjcyMGxzZTNrMWpfMjAyNTAxMDFUMTYwMDAwWiBqaHV0YXJAbQ&ctz=UTC",
            "created": "2024-12-20T13:45:53.000Z",
            "updated": "2024-12-20T13:45:53.282Z",
            "summary": "Test2",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@gmail.com", "self": True},
            "start": {"dateTime": "2025-01-01T16:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2025-01-01T17:00:00Z", "timeZone": "Europe/Prague"},
            "recurringEventId": "7eedg0m1svpv1v62720lse3k1j",
            "originalStartTime": {
                "dateTime": "2025-01-01T16:00:00Z",
                "timeZone": "Europe/Prague",
            },
            "iCalUID": "7eedg0m1svpv1v62720lse3k1j@google.com",
            "sequence": 0,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3469404706564000"',
            "id": "7eedg0m1svpv1v62720lse3k1j_20250102T160000Z",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=N2VlZGcwbTFzdnB2MXY2MjcyMGxzZTNrMWpfMjAyNTAxMDJUMTYwMDAwWiBqaHV0YXJAbQ&ctz=UTC",
            "created": "2024-12-20T13:45:53.000Z",
            "updated": "2024-12-20T13:45:53.282Z",
            "summary": "Test2",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@gmail.com", "self": True},
            "start": {"dateTime": "2025-01-02T16:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2025-01-02T17:00:00Z", "timeZone": "Europe/Prague"},
            "recurringEventId": "7eedg0m1svpv1v62720lse3k1j",
            "originalStartTime": {
                "dateTime": "2025-01-02T16:00:00Z",
                "timeZone": "Europe/Prague",
            },
            "iCalUID": "7eedg0m1svpv1v62720lse3k1j@google.com",
            "sequence": 0,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3469404706564000"',
            "id": "7eedg0m1svpv1v62720lse3k1j_20250103T160000Z",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=N2VlZGcwbTFzdnB2MXY2MjcyMGxzZTNrMWpfMjAyNTAxMDNUMTYwMDAwWiBqaHV0YXJAbQ&ctz=UTC",
            "created": "2024-12-20T13:45:53.000Z",
            "updated": "2024-12-20T13:45:53.282Z",
            "summary": "Test2",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@gmail.com", "self": True},
            "start": {"dateTime": "2025-01-03T16:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2025-01-03T17:00:00Z", "timeZone": "Europe/Prague"},
            "recurringEventId": "7eedg0m1svpv1v62720lse3k1j",
            "originalStartTime": {
                "dateTime": "2025-01-03T16:00:00Z",
                "timeZone": "Europe/Prague",
            },
            "iCalUID": "7eedg0m1svpv1v62720lse3k1j@google.com",
            "sequence": 0,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3469404706564000"',
            "id": "7eedg0m1svpv1v62720lse3k1j_20250104T160000Z",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=N2VlZGcwbTFzdnB2MXY2MjcyMGxzZTNrMWpfMjAyNTAxMDRUMTYwMDAwWiBqaHV0YXJAbQ&ctz=UTC",
            "created": "2024-12-20T13:45:53.000Z",
            "updated": "2024-12-20T13:45:53.282Z",
            "summary": "Test2",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@gmail.com", "self": True},
            "start": {"dateTime": "2025-01-04T16:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2025-01-04T17:00:00Z", "timeZone": "Europe/Prague"},
            "recurringEventId": "7eedg0m1svpv1v62720lse3k1j",
            "originalStartTime": {
                "dateTime": "2025-01-04T16:00:00Z",
                "timeZone": "Europe/Prague",
            },
            "iCalUID": "7eedg0m1svpv1v62720lse3k1j@google.com",
            "sequence": 0,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3470837371874000"',
            "id": "4q17ltu2sr4s2535lsufmpkjkp",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=NHExN2x0dTJzcjRzMjUzNWxzdWZtcGtqa3Agamh1dGFyQG0&ctz=UTC",
            "created": "2024-12-28T20:40:07.000Z",
            "updated": "2024-12-28T20:44:45.937Z",
            "summary": "Test1",
            "location": "Brno, Česko",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@gmail.com", "self": True},
            "start": {"dateTime": "2024-12-29T11:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2024-12-29T11:30:00Z", "timeZone": "Europe/Prague"},
            "iCalUID": "4q17ltu2sr4s2535lsufmpkjkp@google.com",
            "sequence": 0,
            "attendees": [
                {
                    "email": "jhutar@gmail.com",
                    "organizer": True,
                    "self": True,
                    "responseStatus": "accepted",
                }
            ],
            "attendeesOmitted": True,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3470837509568000"',
            "id": "_6co30db661j6abb660sjcb9kcgp66b9p65j3ab9i64p3ec9j70s64c9ic4",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=XzZjbzMwZGI2NjFqNmFiYjY2MHNqY2I5a2NncDY2YjlwNjVqM2FiOWk2NHAzZWM5ajcwczY0YzlpYzQgamh1dGFyQG0&ctz=UTC",
            "created": "2024-12-28T20:45:54.000Z",
            "updated": "2024-12-28T20:45:54.784Z",
            "summary": "Test3",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@seznam.cz"},
            "start": {"dateTime": "2024-12-29T13:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2024-12-29T14:00:00Z", "timeZone": "Europe/Prague"},
            "iCalUID": "3005f0fe-f096-4d2c-91f5-21271388b12a",
            "sequence": 0,
            "attendees": [
                {
                    "email": "jhutar@gmail.com",
                    "self": True,
                    "responseStatus": "needsAction",
                }
            ],
            "guestsCanInviteOthers": False,
            "privateCopy": True,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
        {
            "kind": "calendar#event",
            "etag": '"3470837613312000"',
            "id": "_6so68c1g75h62bb66gq3ib9k71gm8b9pcgs3abb36srmcob36dgjiopn74",
            "status": "confirmed",
            "htmlLink": "https://www.google.com/calendar/event?eid=XzZzbzY4YzFnNzVoNjJiYjY2Z3EzaWI5azcxZ204YjlwY2dzM2FiYjM2c3JtY29iMzZkZ2ppb3BuNzQgamh1dGFyQG0&ctz=UTC",
            "created": "2024-12-28T20:46:41.000Z",
            "updated": "2024-12-28T20:46:46.656Z",
            "summary": "Test4",
            "creator": {"email": "jhutar@gmail.com", "self": True},
            "organizer": {"email": "jhutar@seznam.cz"},
            "start": {"dateTime": "2024-12-29T14:00:00Z", "timeZone": "Europe/Prague"},
            "end": {"dateTime": "2024-12-29T15:00:00Z", "timeZone": "Europe/Prague"},
            "iCalUID": "70d009ba-f449-48ad-9d85-c77fac3a9c79",
            "sequence": 0,
            "attendees": [
                {
                    "email": "jhutar@gmail.com",
                    "self": True,
                    "responseStatus": "declined",
                }
            ],
            "guestsCanInviteOthers": False,
            "privateCopy": True,
            "reminders": {"useDefault": True},
            "eventType": "default",
        },
    ],
}


class TestCalendar(unittest.TestCase):
    def test_get_data(self):
        # This allows calendar.events().list().execute() calls
        mocked_calendar = Mock()
        mocked_calendar \
            .events.return_value \
            .list.return_value \
            .execute.return_value = CAL_FIRST

        def mocked_refresh_credentials(self):
            self.calendar = mocked_calendar

        with patch.object(
            meetings_notifier.my_calendar.MyCalendar,
            "_refresh_credentials",
            mocked_refresh_credentials,
        ) as mock_populate:
            calendar = meetings_notifier.my_calendar.MyCalendar()
            self.assertEqual(len(calendar.events), 10)
            self.assertEqual(type(calendar.events[0]["start"]["dateTime"]), datetime.datetime)
            self.assertEqual(type(calendar.events[0]["end"]["dateTime"]), datetime.datetime)
