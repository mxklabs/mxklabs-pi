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

BoundingBox = collections.namedtuple("BoundingBox",
    ["left","top","width", "height"])

ClockHandParams = collections.namedtuple("ClockHandParams",
    ["colour", "front_depth_pc", "back_depth_pc", "thickness_pc"])

WIDTH = 800
HEIGHT = 480

BACKGROUND_COLOUR = (0, 0, 0, 1)
TILE_OUTLINE_COLOUR = (1, 1, 1, 1)

CLOCK_HOUR_TICK_COLOUR = (1,1,1,1)
CLOCK_HOUR_TICK_DEPTH_PC = 0.03
CLOCK_HOUR_TICK_THICKNESS_PC = 0.01

CLOCK_MINUTE_TICK_COLOUR = (0.5,0.5,0.5,1)
CLOCK_MINUTE_TICK_DEPTH_PC = 0.01
CLOCK_MINUTE_TICK_THICKNESS_PC = 0.01

CLOCK_MINUTE_HAND_PARAMS = ClockHandParams(colour=(0,0,1,0.5),
    front_depth_pc=0.42, back_depth_pc=0.05, thickness_pc=0.02)

CLOCK_HOUR_HAND_PARAMS = ClockHandParams(colour=(1,0,0,0.5),
    front_depth_pc=0.25, back_depth_pc=0.05, thickness_pc=0.03)

MARGIN = 10

#class CairoContext(context)

class ContextRestorer(object):

    def __init__(self, context):
        self._context = context
        self._matrix = None

    def __enter__(self):
        self._matrix = self._context.get_matrix()
        return None

    def __exit__(self, type, value, traceback):
        self._context.set_matrix(self._matrix)

class CairoComponent(object):

    def __init__(self, bounding_box):

        self._bb = bounding_box

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
    def get_margin_box(bounding_box, margin=MARGIN):
        """ Return bounding box with margin removed. """
        bb = bounding_box
        result = BoundingBox(
            left=bb.left + margin,
            top=bb.top + margin,
            width=bb.width - 2*margin,
            height=bb.height - 2*margin)
        return result

class Clock(CairoComponent):

    def __init__(self, bounding_box):
        CairoComponent.__init__(self, bounding_box)
        self._margin_bb = CairoComponent.get_margin_box(self._bb)
        self._real_bb = CairoComponent.get_square_box(self._margin_bb)
        self._unit = self._real_bb.width

    def render(self, context):

        now = datetime.datetime.now()

        with ContextRestorer(context):


            #context.rectangle(real_box.left, real_box.top, real_box.width, real_box.height)
            #context.set_source_rgba(*TILE_OUTLINE_COLOUR)
            #context.stroke()

            context.translate(
                self._real_bb.left + self._real_bb.width / 2,
                self._real_bb.top + self._real_bb.height / 2)

            for i in range(0,60):
                with ContextRestorer(context):
                    # Rotate to this tick.
                    context.rotate((i*math.pi)/30)

                    # We draw hour ticks differently to minute ticks.
                    is_hour_tick = (i % 5) == 0

                    if is_hour_tick:
                        tick_colour = CLOCK_HOUR_TICK_COLOUR
                        tick_depth_pc = CLOCK_HOUR_TICK_DEPTH_PC
                        tick_thickness_pc = CLOCK_HOUR_TICK_THICKNESS_PC

                    else:
                        tick_colour = CLOCK_MINUTE_TICK_COLOUR
                        tick_depth_pc = CLOCK_MINUTE_TICK_DEPTH_PC
                        tick_thickness_pc = CLOCK_MINUTE_TICK_THICKNESS_PC

                    context.set_source_rgba(*tick_colour)
                    context.rectangle(-(self._unit*tick_thickness_pc)/2,
                                      self._unit/2 - (self._unit * tick_depth_pc),
                                      self._unit * tick_thickness_pc,
                                      self._unit * tick_depth_pc)
                    context.fill()

            # Draw hour hand.
            self.draw_hand(context,
                           now.hour * math.pi / 6,
                           CLOCK_HOUR_HAND_PARAMS)

            # Draw minute hand.
            self.draw_hand(context,
                           now.minute * math.pi / 30,
                           CLOCK_MINUTE_HAND_PARAMS)


    def draw_hand(self, context, rotation, params):

        with ContextRestorer(context):

            context.rotate(rotation)
            context.set_source_rgba(*params.colour)
            context.rectangle(-(self._unit * params.thickness_pc) / 2,
                              -(self._unit / 2 - self._unit * params.front_depth_pc),
                              (self._unit * params.thickness_pc),
                              self._unit * (params.front_depth_pc + params.back_depth_pc))
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

        self._clock = Clock(BoundingBox(0, 0, WIDTH, HEIGHT))
        #self.render()
        #self._image_ref = ImageTk.PhotoImage(Image.frombuffer("RGBA", (w, h), self.surface.get_data(), "raw", "BGRA", 0, 1))

        self.label = Label(self)
        self.label.pack(expand=True, fill="both")

        while True:
            self.update_idletasks()
            self.update()
            self.render()
            time.sleep(5)

    def render(self):

        self.context.rectangle(0, 0, WIDTH, HEIGHT)
        self.context.set_source_rgba(*BACKGROUND_COLOUR)
        self.context.fill()


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
