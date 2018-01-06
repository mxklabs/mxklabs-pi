from __future__ import print_function

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

import cairocffi as cairo

import timelineplugin

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = './credentials/google-api/client_secret.json'
APPLICATION_NAME = 'mxk'

flags = False

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

class GoogleCalendarTimelineItem(timelineplugin.TimelineItem):

    def __init__(self, event):
        self._event = event
        datetime_format = '%Y-%m-%dT%H:%M:%SZ'
        timelineplugin.TimelineItem.__init__(self,
            self._event['id'],
            datetime.datetime.strptime(self._event['start']['dateTime'], datetime_format),
            datetime.datetime.  strptime(self._event['end']['dateTime'], datetime_format))


class GoogleCalendar(timelineplugin.TimelinePlugin):

    def __init__(self):
        self._last_event_retrieval_time = None
        self._events = []

    def get_timeline_items(self, start, end):

        now = datetime.datetime.now()

        if self._last_event_retrieval_time is None or (self._last_event_retrieval_time - now).total_seconds() > 120:

            print("RETRIEVING CALENDAR EVENTS FROM GOOGLE")
            self._last_event_retrieval_time = now

            credentials = get_credentials()

            now = datetime.datetime.utcnow().isoformat() + 'Z'
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)

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

    #def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    '''
    credentials = get_credentials()

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    
    #calendars = service.calendars.list()
    
    
    if True:
        eventsResult = service.events().list(
            calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
    
        if not events:
            print('No upcoming events found.')
        for event in events:
            pp = pprint.PrettyPrinter()
            pp.pprint(event)
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
    '''

