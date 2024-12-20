import datetime
import logging
import os
import time

import googleapiclient.discovery
import oauth2client.file
import oauth2client.client
import oauth2client.tools
from httplib2 import Http
from concurrent.futures import TimeoutError

secret_file="client_secret.json"
scope="https://www.googleapis.com/auth/calendar.events.readonly"

class MyCalendar():
    def __init__(self):
        self._credentials_failed = 0
        self._get_calendar()

    def _refresh_credentials(self):
        # If modifying the scope, delete the file token.json.
        token_file = 'token.json'
        if not os.path.exists(token_file):
            with open(token_file, 'a'):
                os.utime(token_file, None)
        store = oauth2client.file.Storage(token_file)

        # Read the credentials in
        logging.info("Authentication to google calendar api")
        creds = store.get()
        if not creds or creds.invalid:
            flow = oauth2client.client.flow_from_clientsecrets(
                secret_file,
                scope,
            )
            flags = oauth2client.tools.argparser.parse_args([])
            creds = oauth2client.tools.run_flow(flow, store, flags)

        # Build the calendar object
        logging.info("Building google calendar API object")
        self.calendar = googleapiclient.discovery.build(
            'calendar',
            'v3',
            http=creds.authorize(Http()),
            cache_discovery=False,
        )

    def _get_calendar(self):
        self._refresh_credentials()

        # Get data from API
        now = datetime.datetime.now(datetime.timezone.utc)
        inaweek = now + datetime.timedelta(days=7)
        while True:
            try:
                data = self.calendar.events().list(
                    calendarId="primary",
                    singleEvents=True,
                    timeMin=now.isoformat(),
                    timeMax=inaweek.isoformat(),
                    maxAttendees=1,
                    maxResults=100,
                    timeZone="UTC",
                ).execute()
            except oauth2client.client.HttpAccessTokenRefreshError as e:
                logging.warning(f"API call failed ({self._credentials_failed}): {e}")
                if self._credentials_failed >= 5:
                    raise
                else:
                    time.sleep(10)
                    self._credentials_failed += 1
                    self._refresh_credentials()
            else:
                self._credentials_failed = 0
                break

        self.events = []
        for event in data["items"]:
            if event["status"] != "confirmed":
                continue

            # If I created the meeting it might not have a attendees
            if "creator" in event and event["creator"]["self"]:
                logging.debug(f"Loaded event {event['summary']} ({event['start']} - {event['end']})")
                self.events.append(event)
                continue

            if "attendees" in event:
                for attendee in event["attendees"]:
                    if attendee["self"]:
                        if attendee["responseStatus"] in ("accepted", "tentative"):
                            logging.debug(f"Loaded event {event['summary']} ({event['start']} - {event['end']})")
                            self.events.append(event)
                        break
                continue

            logging.warning(f"Failed to process event: {event}")

    def get_closest_meeting(self):
        return {}
