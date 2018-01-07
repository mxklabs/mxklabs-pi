import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')

from gi.repository import Gtk
from gi.repository import WebKit

import urllib.parse as urlparse

BASE_URL = 'https://accounts.google.com/o/oauth2/token'
CLIENT_ID = '546482784531-pecfdpigb6ddmkuclmktsne36lc3fdfs.apps.googleusercontent.com'
CALLBACK_URL = 'http://localhost'


class AuthWin(Gtk.Window):
    def __init__(self):
        super(AuthWin, self).__init__()

        oauth_url = "{0}/client_id={1}&redirect_uri={2}&scope=read%20write".format(
                    BASE_URL, CLIENT_ID, CALLBACK_URL)

        self.web = WebKit.WebView()
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.add(self.web)
        self.add(self.scrolled)

        self.set_size_request(900, 640)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title("Authorize")
        self.set_skip_taskbar_hint(True)
        self.set_resizable(False)
        self.set_default_size(900, 640)
        self.web.load_uri(oauth_url)
        self.show_all()
        self.web.connect('navigation-policy-decision-requested',
                         self.navigation_callback)

    def navigation_callback(self, view, frame, request, action, decision):
        url = request.get_uri()
        if "#access_token" in url:
            self.hide()
            res = urlparse.parse_qs(url)
            token_type = res['token_type'][0]
            expires_in = res['expires_in'][0]
            access_token = res[CALLBACK_URL + '/#access_token'][0]

            print(access_token)
            return token_type, expires_in, access_token

win = AuthWin()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()