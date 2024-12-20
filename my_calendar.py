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
                    orderBy="startTime",
                    singleEvents=True,
                    timeMin=now.isoformat(),
                    timeMax=inaweek.isoformat(),
                    maxAttendees=1,
                    maxResults=100,
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

        import pprint
        pprint.pprint(data)

    def get_closest_meeting(self):
        return {}
