from __future__ import print_function

import argparse
import datetime
import httplib2
import apiclient
import oauth2client.client
import oauth2client.file
import oauth2client.tools
import os
import threading
import time

import cairocffi as cairo

import plugins.plugin as plugin


class GoogleCalendarTimelineItem(plugin.TimelineItem):

    STRPTIME_FMT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, event):
        self._event = event
        plugin.TimelineItem.__init__(self)

    def id(self):
        return self._event['id']

    def start(self):
        return datetime.datetime.strptime(self._event['start']['dateTime'],
                                          GoogleCalendarTimelineItem.STRPTIME_FMT)

    def end(self):
        return datetime.datetime.strptime(self._event['end']['dateTime'],
                                          GoogleCalendarTimelineItem.STRPTIME_FMT)

    def event(self):
        return self._event


class GoogleCalendarPlugin(plugin.Plugin):

    def __init__(self, config):
        self._config = config
        self._last_event_retrieval_time = None
        self._events = []
        self._thread = threading.Thread(target=self.run)
        self._thread_stop = threading.Event()
        plugin.Plugin.__init__(self)

    def authenticate(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        # Fake parseargs.
        parser = argparse.ArgumentParser(parents=[oauth2client.tools.argparser])
        flags = parser.parse_args([])

        store = oauth2client.file.Storage(self._config.saved_credentials_file)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = oauth2client.client.flow_from_clientsecrets(
                self._config.client_secret_file,
                self._config.scope)
            flow.user_agent = self._config.application_name
            credentials = oauth2client.tools.run_flow(flow, store, flags)

            print('Storing credentials to ' + self._config.saved_credentials_file)

        return credentials



    def get_timeline_items(self, start, end):

        now = datetime.datetime.now()

        if self._last_event_retrieval_time is None or \
                (now - self._last_event_retrieval_time).total_seconds() > self._config.update_frequency_in_seconds:

            print("RETRIEVING CALENDAR EVENTS FROM GOOGLE")
            self._last_event_retrieval_time = now

            credentials = self.authenticate()

            start_in = start.isoformat() + 'Z'
            end_in = end.isoformat() + 'Z'

            now = datetime.datetime.utcnow().isoformat() + 'Z'
            http = credentials.authorize(httplib2.Http())
            service = apiclient.discovery.build('calendar', 'v3', http=http)

            # 'Z' indicates UTC time
            #print('Getting the upcoming 10 events')

            # calendars = service.calendars.list()

            eventsResult = service.events().list(
                calendarId='primary', timeMin=start_in, timeMax=end_in, maxResults=10,
                singleEvents=True,
                orderBy='startTime').execute()

            events = eventsResult.get('items', [])

            self._events = [GoogleCalendarTimelineItem(event) for event in events]

        return self._events


    def render_on_clockface(self, cairo_context, timeline_item, point_generator, line_generator):

        points = line_generator(timeline_item.start(), timeline_item.end())

        print(timeline_item.event())

        assert(len(points)>=2)
        cairo_context.move_to(*points[0])
        for point in points[1:]:
            cairo_context.line_to(*point)

        #cairo_context.arc(*arc.centre, arc.radius, arc.start_angle, arc.end_angle)
        cairo_context.set_source_rgba(1,0,0,1)
        cairo_context.set_line_width(10)
        cairo_context.set_dash([],0)
        cairo_context.set_line_cap(cairo.constants.LINE_CAP_ROUND)
        cairo_context.stroke()

    def run(self):
        while not self._thread_stop.is_set():
            print("Hi")
            self._thread_stop.wait(5)

    def start(self):
        self._thread.start()

    def stop(self):
        self._thread_stop.set()
        self._thread.join()






