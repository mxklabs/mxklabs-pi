import datetime

import cairocffi as cairo
import datetime
import dotmap

import common
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

nr_suffix = \
{
    0 : "th",
    1 : "st",
    2 : "nd",
    3 : "rd",
    4 : "th",
    5 : "th",
    6 : "th",
    7 : "th",
    8 : "th",
    9 : "th",
}

cfg = dotmap.DotMap(
{
    'timespan' : datetime.timedelta(hours=24*5),

    'window' :
    {
        'width' : 800,
        'height' : 480,
        'background_colour' : (0, 0, 0, 1)
    },

    'app_heading' :
    {
        'bounding_box':
        {
            'left': 0,
            'top': 0,
            'width': 800,
            'height': 40
        },

        'fill' :
        {
            'colour' : (1, 1, 1, 1)
        },

        'stroke' : None,

        'text_fn' : lambda : datetime.datetime.now().strftime("  %A, %d{} of %B %Y").format(nr_suffix[datetime.datetime.now().day%10]),

        'font' :
        {
            'colour' : (0, 0, 0, 1),
            'font_size' : 30,
            'font_face' : ("FreeMono", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL),
            'height': 30
        },
    },

    'clock' :
    {
        'bounding_box' :
        {
            'left' : 20,
            'top' : 70,
            'width' : 390,
            'height' : 390
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
                'colour' : (1, 1, 1, 1)
            },
            'stroke' :
            {
                'colour' : (0, 0, 0, 1),
                'line_width' : 1,
                'dash_style' : ([], 0),
                'line_cap' : cairo.constants.LINE_CAP_BUTT
            },
            'front_depth_pc' : 0.40,
            'back_depth_pc' : 0.05,
            'front_thickness_pc' : 0.015,
            'back_thickness_pc' : 0.03
        },

        'minute_hand' :
        {
            'fill' :
            {
                'colour' : (0.5, 0.5, 1, 1)
            },
            'stroke' :
            {
                'colour' : (0, 0, 0, 1),
                'line_width' : 1,
                'dash_style' : ([], 0),
                'line_cap' : cairo.constants.LINE_CAP_BUTT
            },
            'front_depth_pc' : 0.51,
            'back_depth_pc' : 0.05,
            'front_thickness_pc' : 0.02,
            'back_thickness_pc' : 0.02
        },
    },

    'timeline' :
    {
        'bounding_box' :
        {
            'left' : 20,
            'top' : 70,
            'width' : 390,
            'height' : 390
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
        'today_header_text_fn' : (lambda : "Today"),
        'tomorrow_header_text_fn' : (lambda : "Tomorrow"),
        'datetime_header_text_fn' : (lambda dt : days[dt.weekday()]),

        'bounding_box' :
        {
            'left' : 520,
            'top' : 40,
            'width' : 300,
            'height' : 400
        },

        'heading' :
        {
            'colour' : (1, 1, 1, 1),
            'font_size' : 24,
            'font_face' : ("Deja Vu", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL),
            'height': 40
        },

        'event':
        {
            'colour' : (1, 1, 1, 1),
            'font_size' : 16,
            'font_face' : ("Deja Vu", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
            'height': 20
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
