# For python3, linux I did:
# pip install Pillow
# apt-get install python3-tk
# apt-get install python3-cairo
# pip install cairocffi

import argparse
import collections
import math

from tkinter import Tk, Label
from PIL import Image, ImageTk
import cairocffi as cairo

BoundingBox = collections.namedtuple("BoundingBox", ["left","top","width", "height"])

BACKGROUND_COLOUR = (0, 0, 0, 1)
TILE_OUTLINE_COLOUR = (1, 1, 1, 1)
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

        self._bounding_box = bounding_box

class Clock(CairoComponent):

    def __init__(self, bounding_box):
        CairoComponent.__init__(self, bounding_box)

    def render(self, context):

        with ContextRestorer(context):
            context.set_source_rgba(*TILE_OUTLINE_COLOUR)

            context.translate(
                self._bounding_box.left + self._bounding_box.width / 2,
                self._bounding_box.top + self._bounding_box.height / 2)

            for i in range(0,60,1):
                with ContextRestorer(context):

                    context.rotate((i*math.pi)/30)

                    if (i % 5) == 0:
                        #print("a {}".format(i))
                        context.rectangle(100,
                                          -2,
                                          30,
                                          4)
                    else:
                        #print("b {}".format(i))
                        context.rectangle(120,
                                          -1,
                                          10,
                                          2)
                    context.fill()

            #context.rectangle(self._bounding_box.left,
            #                  self._bounding_box.top,
            #                  self._bounding_box.width,
            #                  self._bounding_box.height)

            #context.set_source_rgba(*TILE_OUTLINE_COLOUR)
            #context.stroke()




class ExampleGui(Tk):
    def __init__(self, debug, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not debug:
            super().attributes("-fullscreen", True)
            super().config(cursor="none")

        w, h = 800, 480

        self.geometry("{}x{}".format(w, h))

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.context = cairo.Context(self.surface)

        # Draw something
        #self.context.scale(w, h)
        self.context.rectangle(0, 0, w, h)
        self.context.set_source_rgba(*BACKGROUND_COLOUR)
        self.context.fill()

        self._clock = Clock(BoundingBox(left=MARGIN,
                                        top=MARGIN,
                                        width=w - 2*MARGIN,
                                        height=h - 2*MARGIN))



        self._clock.render(self.context)
        #self.context.stroke()
        #self.context.rectangle(1, 1, w-2, h-2)
        #self.context.set_source_rgba(0, 0, 0, 1)
        #self.context.fill()

        #self.context.set_source_rgba(1, 0, 0, 1)
        #self.context.move_to(90, 140)
        #self.context.rotate(-0.5)
        #self.context.set_font_size(32)
        #self.context.show_text(u'HAPPY DONUT!')

        self._image_ref = ImageTk.PhotoImage(Image.frombuffer("RGBA", (w, h), self.surface.get_data(), "raw", "BGRA", 0, 1))

        self.label = Label(self, image=self._image_ref)
        self.label.pack(expand=True, fill="both")

        self.mainloop()


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
