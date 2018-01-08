import datetime

import cairocffi as cairo
import dotmap

import plugins.googlecalendarplugin

cfg = dotmap.DotMap(
{
    'window' :
    {
        'width' : 800,
        'height' : 480,
        'background_colour' : (0, 0, 0, 1)
    },

    'clock' :
    {
        'margin' : 0,

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
        'margin' :  0,
        'thickness' : 25,
        'length' : datetime.timedelta(hours=48),

        'stroke':
        {
            'colour': (0.7, 0.7, 0.7, 1),
            'line_width': 1.5,
            'dash_style': ([], 0),
            'line_cap': cairo.constants.LINE_CAP_BUTT
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
