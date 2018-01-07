from __future__ import print_function

import argparse
import datetime
import httplib2
import apiclient
import oauth2client.client
import oauth2client.file
import oauth2client.tools

import os

import cairocffi as cairo

try:
    import plugins.plugin as plugin
except ImportError:
    import plugin

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'credentials/google-api/client_secret.json'
APPLICATION_NAME = 'mxklabs-pi'


class GoogleCalendarTimelineItem(plugin.TimelineItem):

    def __init__(self, event):
        self._event = event

        datetime_format = '%Y-%m-%dT%H:%M:%SZ'
        id = self._event['id']
        start_datetime = datetime.datetime.strptime(self._event['start']['dateTime'], datetime_format)
        end_datetime = datetime.datetime.strptime(self._event['end']['dateTime'], datetime_format)

        plugin.TimelineItem.__init__(self, id, start_datetime, end_datetime)


class GoogleCalendarPlugin(plugin.Plugin):

    def __init__(self):
        self._last_event_retrieval_time = None
        self._events = []

        plugin.Plugin.__init__(self)

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        # Fake parseargs.
        parser = argparse.ArgumentParser(parents=[oauth2client.tools.argparser])
        flags = parser.parse_args([])

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, 'credentials', 'google-api')

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)

        credential_path = os.path.join(credential_dir,
                                       'google-api-saved-credentials.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
                                                  SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = oauth2client.tools.run_flow(flow, store, flags)

            print('Storing credentials to ' + credential_path)

        return credentials

    def get_timeline_items(self, start, end):

        now = datetime.datetime.now()

        if self._last_event_retrieval_time is None or \
                (now - self._last_event_retrieval_time).total_seconds() > 120:

            print("RETRIEVING CALENDAR EVENTS FROM GOOGLE")
            self._last_event_retrieval_time = now

            credentials = self.get_credentials()

            now = datetime.datetime.utcnow().isoformat() + 'Z'
            http = credentials.authorize(httplib2.Http())
            service = apiclient.discovery.build('calendar', 'v3', http=http)

            # 'Z' indicates UTC time
            #print('Getting the upcoming 10 events')

            # calendars = service.calendars.list()

            eventsResult = service.events().list(
                calendarId='primary', timeMin=now, maxResults=10,
                singleEvents=True,
                orderBy='startTime').execute()

            events = eventsResult.get('items', [])

            self._events = [GoogleCalendarTimelineItem(event) for event in events]

        return self._events


    def render_on_clockface(self, cairo_context, timeline_item, point_generator, line_generator):

        points = line_generator(timeline_item.start(), timeline_item.end())

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


if __name__ == '__main__':
    plugin = GoogleCalendarPlugin()
    plugin.get_credentials()
    print("Done!")




