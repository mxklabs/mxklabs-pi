import datetime

import cairocffi as cairo
import datetime
import dotmap

import common
import plugins.googlecalendarplugin

NR_SUFFIX = \
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

PALETTE = \
{
    'monday' : (0.60, 0.00, 0.00, 1),
    'tuesday' : (0.60, 0.27, 0.00, 1),
    'wednesday' : (0.66, 0.50, 0.01, 1),
    'thursday' : (0.05, 0.54, 0.00, 1),
    'friday' : (0.00, 0.51, 0.35, 1),
    'saturday' : (0.00, 0.39, 0.51, 1),
    'sunday' : (0.51, 0.00, 0.46, 1)
}

def DAY_LABEL_STYLE(day):
    {
        'background':
            {

                'fill':
                    {
                        'colour': PALETTE[day]
                    },
                'stroke':
                    {
                        'colour': (1, 1, 1, 1),
                        'line_width': 1.5,
                        'dash_style': ([], 0),
                        'line_cap': cairo.constants.LINE_CAP_BUTT
                    }
            },

        'font':
            {
                'colour': (1, 1, 1, 1),
                'font_size': 8,
                'font_face': (
                "FreeMono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
                'height': 30
            }
    }

cfg = dotmap.DotMap(
{
    'timespan' : datetime.timedelta(hours=24*6),

    'window' :
    {
        'width' : 800,
        'height' : 480,
        'background_colour' : (0, 0, 0, 1)
    },

    'palette' : PALETTE,

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

        'text_fn' : lambda : datetime.datetime.now().strftime("  %A, %d{} of %B %Y").format(NR_SUFFIX[datetime.datetime.now().day%10]),

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

        'face' :
        {
            'fill' : None,
            'stroke' :
            {
                'colour': (1, 1, 1, 1),
                'line_width': 1.5,
                'dash_style': ([], 0),
                'line_cap': cairo.constants.LINE_CAP_BUTT
            }
        },

        'hour_ticks' :
        {
            'fill' :
            {
                'colour' : (1, 1, 1, 1)
            },
            'stroke' : None,
            'depth_pc' : 0.01,
            'thickness_pc' : 0.01
        },

        'minute_ticks' :
        {
            'fill' :
            {
                'colour' : (0, 0, 0, 0)
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
            'front_depth_pc' : 0.50,
            'back_depth_pc' : 0.05,
            'front_thickness_pc' : 0.01,
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

        'stroke_fn': lambda weekday: dotmap.DotMap(
        {
            'colour': PALETTE[weekday], # not used
            'line_width': 1.5,
            'dash_style': ([], 0),
            'line_cap': cairo.constants.LINE_CAP_BUTT
        }),

        'day_labels' :
        {
            'width' : 24,
            'height' : 12,
            'radius' : 3,

            'day_start_label' :
            {
                'offset' : 13,
                'open_left' : False,
                'open_right' : True,
            },

            'day_end_label' :
            {
                'offset' : -13,
                'open_left' : True,
                'open_right' : False
            },

            'monday' :
            {
                'background' :
                {

                    'fill' :
                    {
                        'colour' : PALETTE['monday']
                    },
                    'stroke' :
                    {
                        'colour': (1, 1, 1, 1),
                        'line_width': 1.5,
                        'dash_style': ([], 0),
                        'line_cap': cairo.constants.LINE_CAP_BUTT
                    }
                },

                'font' :
                {
                    'colour' : (1, 1, 1, 1),
                    'font_size' : 8,
                    'font_face' : ("FreeMono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
                    'height': 30
                }
            },
            'tuesday' :
            {
                'background' :
                {

                    'fill' :
                    {
                        'colour' : PALETTE['tuesday']
                    },
                    'stroke' :
                    {
                        'colour': (1, 1, 1, 1),
                        'line_width': 1.5,
                        'dash_style': ([], 0),
                        'line_cap': cairo.constants.LINE_CAP_BUTT
                    }
                },

                'font' :
                {
                    'colour' : (1, 1, 1, 1),
                    'font_size' : 8,
                    'font_face' : ("FreeMono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
                    'height': 30
                }
            },
            'wednesday' :
            {
                'background' :
                {

                    'fill' :
                    {
                        'colour' : PALETTE['wednesday']
                    },
                    'stroke' :
                    {
                        'colour': (1, 1, 1, 1),
                        'line_width': 1.5,
                        'dash_style': ([], 0),
                        'line_cap': cairo.constants.LINE_CAP_BUTT
                    }
                },

                'font' :
                {
                    'colour' : (1, 1, 1, 1),
                    'font_size' : 8,
                    'font_face' : ("FreeMono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
                    'height': 30
                }
            },
            'thursday' :
            {
                'background' :
                {

                    'fill' :
                    {
                        'colour' : PALETTE['thursday']
                    },
                    'stroke' :
                    {
                        'colour': (1, 1, 1, 1),
                        'line_width': 1.5,
                        'dash_style': ([], 0),
                        'line_cap': cairo.constants.LINE_CAP_BUTT
                    }
                },

                'font' :
                {
                    'colour' : (1, 1, 1, 1),
                    'font_size' : 8,
                    'font_face' : ("FreeMono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
                    'height': 30
                }
            },
            'friday' :
            {
                'background' :
                {

                    'fill' :
                    {
                        'colour' : PALETTE['friday']
                    },
                    'stroke' :
                    {
                        'colour': (1, 1, 1, 1),
                        'line_width': 1.5,
                        'dash_style': ([], 0),
                        'line_cap': cairo.constants.LINE_CAP_BUTT
                    }
                },

                'font' :
                {
                    'colour' : (1, 1, 1, 1),
                    'font_size' : 8,
                    'font_face' : ("FreeMono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
                    'height': 30
                }
            },
            'saturday' :
            {
                'background' :
                {

                    'fill' :
                    {
                        'colour' : PALETTE['saturday']
                    },
                    'stroke' :
                    {
                        'colour': (1, 1, 1, 1),
                        'line_width': 1.5,
                        'dash_style': ([], 0),
                        'line_cap': cairo.constants.LINE_CAP_BUTT
                    }
                },

                'font' :
                {
                    'colour' : (1, 1, 1, 1),
                    'font_size' : 8,
                    'font_face' : ("FreeMono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
                    'height': 30
                }
            },
            'sunday' :
            {
                'background' :
                {

                    'fill' :
                    {
                        'colour' : (0.51, 0.00, 0.46, 1)
                    },
                    'stroke' :
                    {
                        'colour': (1, 1, 1, 1),
                        'line_width': 1.5,
                        'dash_style': ([], 0),
                        'line_cap': cairo.constants.LINE_CAP_BUTT
                    }
                },

                'font' :
                {
                    'colour' : (1, 1, 1, 1),
                    'font_size' : 8,
                    'font_face' : ("FreeMono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD),
                    'height': 30
                }
            }
        }
    },

    'event_list' :
    {
        'today_header_text_fn' : (lambda : "Today"),
        'tomorrow_header_text_fn' : (lambda : "Tomorrow"),
        'datetime_header_text_fn' : (lambda dt : datetime.datetime.strftime(dt, "%A")),

        'bounding_box' :
        {
            'left' : 520,
            'top' : 40,
            'width' : 300,
            'height' : 400
        },

        'heading' :
        {
            'font' :
            {
                'colour' : (1, 1, 1, 1),
                'font_size' : 24,
                'font_face' : ("Deja Vu", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL),
                'height': 40
            }
        },

        'event':
        {
            'font' :
            {
                'colour' : (1, 1, 1, 1),
                'font_size' : 16,
                'font_face' : ("Deja Vu", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL),
                'height': 20
            }
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
