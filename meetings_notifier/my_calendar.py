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
        self.events = []
        self._credentials_failed = 0
        self.refresh_events()

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

        # Get data from API in a loop that handles retries on API errors and paginating
        next_page_token = None
        now = datetime.datetime.now(datetime.timezone.utc)
        inaweek = now + datetime.timedelta(days=7)
        while True:
            try:
                if next_page_token is None:
                    request = self.calendar.events().list(
                        calendarId="primary",
                        singleEvents=True,
                        timeMin=now.isoformat(),
                        timeMax=inaweek.isoformat(),
                        maxAttendees=1,
                        maxResults=250,
                        timeZone="UTC",
                    )
                else:
                    request = self.calendar.events().list_next(
                        previous_request=request,
                        previous_response=data,
                    )
                data = request.execute()
            except oauth2client.client.HttpAccessTokenRefreshError as e:
                logging.warning(f"API call failed ({self._credentials_failed}): {e}")
                if self._credentials_failed >= 5:
                    raise
                else:
                    # API request failed, increment failures counter
                    self._credentials_failed += 1

                    time.sleep(10)
                    self._refresh_credentials()
            else:
                # API request worked, reset failures counter
                self._credentials_failed = 0
                for event in data["items"]:
                    yield event

                next_page_token = data.get('nextPageToken', None)
                if next_page_token is None:
                    break

    def _filtered_events(self):
        for event in self._get_calendar():
            if "eventType" in event and event["eventType"] in ("workingLocation",):
                continue

            if event["status"] != "confirmed":
                continue

            # If I created the meeting it might not have a attendees
            if "creator" in event and "self" in event["creator"] and event["creator"]["self"]:
                yield event
                continue

            if "attendees" in event:
                for attendee in event["attendees"]:
                    if "self" in attendee and attendee["self"]:
                        if attendee["responseStatus"] in ("accepted", "tentative"):
                            yield event
                        break
                continue

            if "start" not in event or "dateTime" not in event["start"]:
                continue

            logging.warning(f"Failed to process event: {event}")

    def _populate_events(self):
        events = []

        for event in self._filtered_events():
            logging.debug(f"Loaded event {event['summary']} ({event['start']} - {event['end']})")
            event["start"]["dateTime"] = datetime.datetime.fromisoformat(event["start"]["dateTime"])
            event["end"]["dateTime"] = datetime.datetime.fromisoformat(event["end"]["dateTime"])
            events.append(event)

        return sorted(events, key=lambda x: x['start']['dateTime'])

    def refresh_events(self):
        # TODO: Make this a non blocking thread
        self.events = self._populate_events()
        return True   # Needed for Gtk timer that calls this not to disappear

    def get_closest_meeting(self):
        try:
            return self.events[0]
        except IndexError:
            return {}
