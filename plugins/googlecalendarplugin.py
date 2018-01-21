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

import pprint

import cairocffi as cairo

import plugins.plugin as plugin


class GoogleCalendarTimelineItem(plugin.TimelineItem):

    STRPDATE_FMT = '%Y-%m-%d'
    STRPTIME_FMT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, event, plug):
        self._event = event
        self._plugin = plug
        plugin.TimelineItem.__init__(self)

    def id(self):
        return self._event['id']

    def start(self):
        result = None
        start = self._event['start']
        if 'dateTime' in start:
            result = datetime.datetime.strptime(
                start['dateTime'],
                GoogleCalendarTimelineItem.STRPTIME_FMT)
        elif 'date' in start:
            result = datetime.datetime.strptime(
                start['date'],
                GoogleCalendarTimelineItem.STRPDATE_FMT)
            result.replace(hour=0, minute=0, second=0, microsecond=0)
        return result

    def end(self):
        result = None
        end = self._event['end']
        if 'dateTime' in end:
            result = datetime.datetime.strptime(
                end['dateTime'],
                GoogleCalendarTimelineItem.STRPTIME_FMT)
        elif 'date' in end:
            result = datetime.datetime.strptime(
                end['date'],
                GoogleCalendarTimelineItem.STRPDATE_FMT)
            result.replace(hour=23, minute=59, second=59, microsecond=0)
        return result

    def event(self):
        return self._event

    def plugin(self):
        return self._plugin

    def title(self):
        return self._event['summary']

    def is_all_day_event(self):
        return 'date' in self._event['start']


class GoogleCalendarPlugin(plugin.Plugin):

    def __init__(self, config):
        self._config = config
        self._credentials = None
        self._service = None
        self._events = []
        self._last_start = None
        self._last_end = None
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
        self._credentials = self.get_credentials()

    def get_timeline_items(self, start, end):
        self._last_start = start
        self._last_end = end
        return self._events

    def render_on_clockface(self, cairo_context, start_utc, end_utc, timeline_item, point_generator, line_generator):

        points = line_generator(max(start_utc, timeline_item.start()), min(end_utc, timeline_item.end()))

        assert (len(points) >= 2)
        cairo_context.move_to(*points[0])
        for point in points[1:]:
            cairo_context.line_to(*point)

        if not timeline_item.is_all_day_event():

            #cairo_context.arc(*arc.centre, arc.radius, arc.start_angle, arc.end_angle)
            cairo_context.set_source_rgba(1,0,0,1)
            cairo_context.set_line_width(10)
            cairo_context.set_dash([],0)
            cairo_context.set_line_cap(cairo.constants.LINE_CAP_ROUND)
            cairo_context.stroke()

        else:
            cairo_context.set_source_rgba(1,0,0,1)
            cairo_context.set_line_width(2)
            cairo_context.set_dash([],0)
            cairo_context.set_line_cap(cairo.constants.LINE_CAP_ROUND)
            cairo_context.stroke()

            point1 = point_generator(timeline_item.start())
            point2 = point_generator(timeline_item.end())

            cairo_context.move_to(*point1)
            cairo_context.move_to(*point1)

            cairo_context.set_source_rgba(1, 0, 0, 1)
            cairo_context.set_line_width(10)
            cairo_context.set_dash([], 0)
            cairo_context.set_line_cap(cairo.constants.LINE_CAP_ROUND)
            cairo_context.stroke()

            cairo_context.move_to(*point2)
            cairo_context.move_to(*point2)

            cairo_context.set_source_rgba(1, 0, 0, 1)
            cairo_context.set_line_width(10)
            cairo_context.set_dash([], 0)
            cairo_context.set_line_cap(cairo.constants.LINE_CAP_ROUND)
            cairo_context.stroke()

    def get_credentials(self):
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

    def get_service(self, credentials):
        http = credentials.authorize(httplib2.Http())
        return apiclient.discovery.build('calendar', 'v3', http=http)

    def get_calendars(self, service):
        """
        Get selected calendars from Google Calendar API.
        :param service:
        :return:
        """
        api_result = service.calendarList().list(
            fields='items(id, selected, summary)'
        ).execute()

        return [r for r in api_result['items'] if 'selected' in r]

    def get_events(self, service, calendars, start, end):

        events = []

        pp = pprint.PrettyPrinter()

        for calendar in calendars:

            start_in = start.isoformat() + 'Z'
            end_in = end.isoformat() + 'Z'

            api_result = service.events().list(
                calendarId=calendar['id'],
                timeMin=start_in,
                timeMax=end_in, maxResults=10,
                singleEvents=True,
                orderBy='startTime').execute()

            events += api_result.get('items', [])

        #pp.pprint(events)
        return [GoogleCalendarTimelineItem(event, self) for event in events]

    def get_colours(self, service):
        colorsResult = service.colors().get().execute()
        #print(colorsResult)

        #pp = pprint.PrettyPrinter()
        #pp.pprint(colorsResult)

    def run(self):

        self._credentials = self.get_credentials()
        self._service = self.get_service(self._credentials)
        self._calendars = self.get_calendars(self._service)
        self._colours = self.get_colours(self._service)

        while not self._thread_stop.is_set():

            if self._last_start is not None and self._last_end is not None:
                self._events = self.get_events(self._service, self._calendars, self._last_start, self._last_end)
                self._thread_stop.wait(self._config.update_frequency_in_seconds)
            else:
                self._thread_stop.wait(1)

    def start(self):
        self._thread.start()

    def stop(self):
        self._thread_stop.set()
        self._thread.join()






