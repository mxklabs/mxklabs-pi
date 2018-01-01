# For python3, linux I did:
# pip install Pillow
# apt-get install python3-tk
# apt-get install python3-cairo
# pip install cairocffi

import argparse
import collections
import datetime
import math
import time

from tkinter import Tk, Label
from PIL import Image, ImageTk
import cairocffi as cairo

BoundingBox = collections.namedtuple("BoundingBox", ["left","top","width",
    "height"])

FillParams = collections.namedtuple("FillParams", ["colour"])

StrokeParams = collections.namedtuple("StrokeParams", ["colour", "line_width",
    "dash_style", "line_cap"])

ClockParams = collections.namedtuple("ClockParams", ["margin",
    "hour_tick_params", "minute_tick_params", "hour_hand_params",
    "minute_hand_params"])

ClockTickParams = collections.namedtuple("ClockTickParams", ["fill_params",
    "stroke_params", "depth_pc", "thickness_pc"])

ClockHandParams = collections.namedtuple("ClockHandParams", ["fill_params",
    "stroke_params", "hand_front_depth_pc", "hand_back_depth_pc",
    "hand_thickness_pc"])

ClockExParams = collections.namedtuple("ClockExParams", ["clock_params",
    "margin", "number_of_timeline_segments", "timeline_segment_params"])

TimelineSegmentParams = collections.namedtuple("TimelineSegmentParams", ["clock_params",
    "thickness", "fill_params", "stroke_params"])

WIDTH = 800
HEIGHT = 480

BACKGROUND_COLOUR = (0, 0, 0, 1)
TILE_OUTLINE_COLOUR = (1, 1, 1, 1)

CLOCK_PARAMS = ClockParams(

    margin=5,

    hour_tick_params=ClockTickParams(
        fill_params=FillParams(colour=(1,1,1,1)),
        stroke_params=None,
        depth_pc=0.03,
        thickness_pc=0.01),

    minute_tick_params=ClockTickParams(
        fill_params=FillParams(colour=(0.5,0.5,0.5,1)),
        stroke_params=None,
        depth_pc=0.01,
        thickness_pc=0.01),

    hour_hand_params=ClockHandParams(
        fill_params=None,
        stroke_params=StrokeParams(
            colour=(1, 0, 0, 1),
            line_width=2,
            dash_style=([], 0),
            line_cap=cairo.constants.LINE_CAP_BUTT),
        hand_front_depth_pc=0.35,
        hand_back_depth_pc=0.05,
        hand_thickness_pc=0.02),

    minute_hand_params=ClockHandParams(
        fill_params=FillParams(colour=(1, 1, 1, 1)),
        stroke_params=None,
        hand_front_depth_pc=0.42,
        hand_back_depth_pc=0.05,
        hand_thickness_pc=0.01))

CLOCK_EX_PARAMS = \
{
    'clock' : CLOCK_PARAMS,
    'margin' : 20,

    'timeline' :
    {
        'stroke': StrokeParams(
            colour=(0.5, 0.5, 0.5, 1),
            line_width=1.5,
            dash_style=([], 0),
            line_cap=cairo.constants.LINE_CAP_BUTT),

        'segments' :
        [
            {
                'thickness' : 20,
                'fill' :FillParams(colour=(1, 0, 1, 1))
            },
            {
                'thickness': 20,
                'fill': FillParams(colour=(1, 1, 0, 1)),
            }
        ]
    }
}


class CairoUtils(object):

    @staticmethod
    def set_fill_params(context, fill_params):
        """ Set context to fill_params. """
        context.set_source_rgba(*fill_params.colour)

    @staticmethod
    def set_stroke_params(context, stroke_params):
        """ Set context to stroke_params. """
        context.set_source_rgba(*stroke_params.colour)
        context.set_line_width(stroke_params.line_width)
        context.set_dash(*stroke_params.dash_style)
        context.set_line_cap(stroke_params.line_cap)

    @staticmethod
    def draw(context, params):
        """ Draw fill and/or stroke with params. """
        if params.fill_params and params.stroke_params:
            CairoUtils.set_fill_params(context, params.fill_params)
            context.fill_preserve()
            CairoUtils.set_stroke_params(context, params.stroke_params)
            context.stroke()
        elif params.fill_params:
            CairoUtils.set_fill_params(context, params.fill_params)
            context.fill()
        elif params.stroke_params:
            CairoUtils.set_stroke_params(context, params.stroke_params)
            context.stroke()

    @staticmethod
    def get_square_box(bounding_box):
        """ Return largest square in the bounding box """
        bb = bounding_box
        box_size = min(bb.width, bb.height)
        result = BoundingBox(
            left=bb.left + (bb.width - box_size) / 2,
            top=bb.top + (bb.height - box_size) / 2,
            width=box_size,
            height=box_size)
        return result

    @staticmethod
    def get_margin_box(bounding_box, margin):
        """ Return bounding box with margin removed. """
        print(bounding_box)
        bb = bounding_box
        print(bb)
        print(bb.left)
        print(margin)
        result = BoundingBox(
            left=bb.left + margin,
            top=bb.top + margin,
            width=bb.width - 2 * margin,
            height=bb.height - 2 * margin)
        return result

class ContextRestorer(object):

    def __init__(self, context):
        self._context = context
        self._matrix = None

    def __enter__(self):
        self._matrix = self._context.get_matrix()
        return None

    def __exit__(self, type, value, traceback):
        self._context.set_matrix(self._matrix)

class Clock(object):

    def __init__(self, params, bounding_box):
        self._params = params
        margin_bb = CairoUtils.get_margin_box(
            bounding_box=bounding_box,
            margin=self._params.margin)
        self._real_bb = CairoUtils.get_square_box(margin_bb)
        self._unit = self._real_bb.width

    def render(self, context):

        # Work out the time.
        now = datetime.datetime.now()

        with ContextRestorer(context):

            # Translate to middle of clock face.
            context.translate(
                self._real_bb.left + self._real_bb.width / 2,
                self._real_bb.top + self._real_bb.height / 2)

            # Draw ticks.
            for i in range(0, 60):

                if (i % 5) == 0:
                    tick_params = self._params.hour_tick_params
                else:
                    tick_params = self._params.minute_tick_params

                self.draw_tick(context, i, 60, tick_params)

            # Draw hour hand.
            self.draw_hand(context, now.hour * 60 + now.minute, 12 * 60, self._params.hour_hand_params)

            # Draw minute hand.
            self.draw_hand(context, now.minute, 60, self._params.minute_hand_params)

    def draw_tick(self, context, num, den, params):

        with ContextRestorer(context):
            rotation = (2 * math.pi) * (num / den)
            context.rotate(rotation)

            context.rectangle(-(self._unit * params.thickness_pc) / 2,
                              self._unit / 2 - (self._unit * params.depth_pc),
                              self._unit * params.thickness_pc,
                              self._unit * params.depth_pc)

            CairoUtils.draw(context, params)

    def draw_hand(self, context, num, den, params):

        with ContextRestorer(context):
            rotation = (2 * math.pi) * (num / den)
            context.rotate(rotation)

            context.rectangle(
                -(self._unit * params.hand_thickness_pc) / 2,
                -(self._unit * params.hand_front_depth_pc),
                 (self._unit * params.hand_thickness_pc),
                 (self._unit * (params.hand_front_depth_pc
                    + params.hand_back_depth_pc)))

            CairoUtils.draw(context, params)

class ClockEx(object):

    def __init__(self, params, bounding_box):

        self._params = params
        self._bb = CairoUtils.get_square_box(
            CairoUtils.get_margin_box(
                bounding_box=bounding_box,
                margin=self._params['margin']))
        self._unit = self._bb.width
        self._centre = (self._bb.left + self._bb.width / 2,
                        self._bb.top + self._bb.height / 2)


        timeline_segments = self._params['timeline']['segments']
        timeline_margin = sum([ts['thickness'] for ts in timeline_segments])

        self._clock_bb = CairoUtils.get_margin_box(
            self._bb,
            margin=timeline_margin)
        self._clock_unit = self._clock_bb.width

        self._clock = Clock(self._params['clock'], self._clock_bb)

    def render(self, context):
        self._clock.render(context)

        radius = self._clock_unit / 2

        CairoUtils.set_stroke_params(context, self._params['timeline']['stroke'])
        context.arc(*self._centre, radius, 0, 2 * math.pi)
        context.stroke()

        for ts in self._params['timeline']['segments']:
            radius += ts['thickness']
            context.arc(*self._centre, radius, 0, 2 * math.pi)
            context.stroke()

class ExampleGui(Tk):
    def __init__(self, debug, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not debug:
            super().attributes("-fullscreen", True)
            super().config(cursor="none")

        w, h = WIDTH, HEIGHT

        self.geometry("{}x{}".format(w, h))

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.context = cairo.Context(self.surface)


        # Draw something
        #self.context.scale(w, h)

        #self.context.set_source_rgba(1, 0, 0, 1)
        #self.context.move_to(90, 140)
        #self.context.rotate(-0.5)
        #self.context.set_font_size(32)
        #self.context.show_text(u'HAPPY DONUT!')

        bounding_box = BoundingBox(
            left=20,
            top=20,
            width=440,
            height=440)

        self._clock = ClockEx(CLOCK_EX_PARAMS, bounding_box)
        #self.render()
        #self._image_ref = ImageTk.PhotoImage(Image.frombuffer("RGBA", (w, h), self.surface.get_data(), "raw", "BGRA", 0, 1))

        self.label = Label(self)
        self.label.pack(expand=True, fill="both")

        while True:
            self.render()
            self.update_idletasks()
            self.update()
            time.sleep(5)

    def render(self):

        self.context.set_operator(cairo.constants.OPERATOR_OVER)

        self.context.rectangle(0, 0, WIDTH, HEIGHT)
        self.context.set_source_rgba(*BACKGROUND_COLOUR)
        self.context.fill()

        self.context.set_operator(cairo.constants.OPERATOR_SCREEN)

        self._clock.render(self.context)

        new_img = Image.frombuffer("RGBA", (WIDTH, HEIGHT),
                                   self.surface.get_data(),
                                   "raw","BGRA", 0, 1)
        new_tk_img = ImageTk.PhotoImage(new_img)

        self.label.configure(image=new_tk_img)
        self.label.image = new_tk_img
        #panel.image = img2




if __name__ == "__main__":
    """
    Using the argparse module to ease the development process of this source
    code a little. Start this file with command-line argument '--mode debug' to
    avoid going in fullscreen mode and to avoid hiding the cursor.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['release', 'debug'], default='release')

    args = parser.parse_args()

    ExampleGui(debug=(args.mode == 'debug'))
