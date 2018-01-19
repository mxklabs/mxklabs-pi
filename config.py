import datetime

import cairocffi as cairo
import datetime
import dotmap

import plugins.googlecalendarplugin

days = \
{
    0 : "Monday",
    1 : "Tuesday",
    2 : "Wednesday",
    3 : "Thursday",
    4 : "Friday",
    5 : "Saturday",
    6 : "Sunday"
}

cfg = dotmap.DotMap(
{
    'timespan' : datetime.timedelta(hours=24*7),

    'window' :
    {
        'width' : 800,
        'height' : 480,
        'background_colour' : (0, 0, 0, 1)
    },

    'clock' :
    {
        'bounding_box' :
        {
            'left' : 20,
            'top' : 20,
            'width' : 440,
            'height' : 440
        },

        'hour_ticks' :
        {
            'fill' :
            {
                'colour' : (1,1,1,1)
            },
            'stroke' : None,
            'depth_pc' : 0.03,
            'thickness_pc' : 0.01
        },

        'minute_ticks' :
        {
            'fill' :
            {
                'colour' : (0.5,0.5,0.5,1)
            },
            'stroke' : None,
            'depth_pc' : 0.01,
            'thickness_pc' : 0.01
        },

        'hour_hand' :
        {
            'fill' :
            {
                'colour' : (1, 1, 1, 0.5)
            },
            'stroke' :
            {
                'colour' : (0, 0, 0, 1),
                'line_width' : 2,
                'dash_style' : ([], 0),
                'line_cap' : cairo.constants.LINE_CAP_BUTT
            },
            'front_depth_pc' : 0.30,
            'back_depth_pc' : 0.05,
            'thickness_pc' : 0.03
        },

        'minute_hand' :
        {
            'fill' :
            {
                'colour' : (0.5, 0.5, 1, 0.5)
            },
            'stroke' :
            {
                'colour' : (0, 0, 0, 1),
                'line_width' : 2,
                'dash_style' : ([], 0),
                'line_cap' : cairo.constants.LINE_CAP_BUTT
            },
            'front_depth_pc' : 0.50,
            'back_depth_pc' : 0.04,
            'thickness_pc' : 0.02,
        },
    },

    'timeline' :
    {
        'bounding_box' :
        {
            'left' : 20,
            'top' : 20,
            'width' : 440,
            'height' : 440
        },

        'thickness' : 15,

        'stroke':
        {
            'colour': (0.7, 0.7, 0.7, 1),
            'line_width': 1.5,
            'dash_style': ([], 0),
            'line_cap': cairo.constants.LINE_CAP_BUTT
        }
    },

    'event_list' :
    {
        'header_text_fn' : (lambda dt : days[dt.weekday()]),

        'bounding_box' :
        {
            'left' : 480,
            'top' : 20,
            'width' : 300,
            'height' : 440
        },

        'heading' :
        {
            'colour' : (1, 1, 1, 1),
            'font_size' : 20,
            'font_face' : ("Deja Vu", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL),
            'height': 30
        },

        'event':
        {
            'colour' : (1, 1, 1, 1),
            'font_size' : 10,
            'font_face' : ("Deja Vu", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
            'height': 14
        }
    },

    'plugins':
    [
        {
            'plugin' : plugins.googlecalendarplugin.GoogleCalendarPlugin,
            'config' :
            {
                'scope' : 'https://www.googleapis.com/auth/calendar.readonly',
                'client_secret_file' : './credentials/google-api/client_secret.json',
                'saved_credentials_file' : './credentials/google-api/saved_credentials.json',
                'application_name' : 'mxklabs-pi',
                'update_frequency_in_seconds' : 120
            }
        }
    ]
})
