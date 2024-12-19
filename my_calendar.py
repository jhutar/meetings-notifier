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
        self._get_calendar()

    def _get_calendar(self):
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

        print(self.calendar)
        print(dir(self.calendar))
        now = datetime.datetime.now(datetime.timezone.utc)
        tomorrow = now + datetime.timedelta(days=6)

        try:
            data = self.calendar.events().list(
                calendarId="primary",
                orderBy="startTime",
                singleEvents=True,
                timeMin=now.isoformat(),
                timeMax=tomorrow.isoformat(),
                maxAttendees=1,
                maxResults=3,
            ).execute()
        except oauth2client.client.HttpAccessTokenRefreshError as e:
            logging.warning("{} (will try again)".format(repr(e)))
            #### TODO: Refresh token
            ###time.sleep(10)
            ###self._get_calendar()
            ###if cycle < 5:
            ###    return self.query_free_busy_api(people, start, end, cycle)
            ###else:
            ###    LOG.warning("Token wasn't successfully refreshed")
            ###    raise TimeoutError

        import pprint
        pprint.pprint(data)

    def get_closest_meeting(self):
        return {}
