# For python3, linux I did:
# pip install Pillow
# apt-get install python3-tk
# apt-get install python3-cairo
# pip install cairocffi

import argparse

from tkinter import Tk, Label
from PIL import Image, ImageTk
import cairocffi as cairo

BACKGROUND_COLOUR = (0, 0, 0, 1)
TILE_OUTLINE_COLOUR = (1, 1, 1, 1)
MARGIN            = 10

def draw_tile(ctx, l, r, w, h):
    ctx.move_to(l, r)
    ctx.rectangle(l, r, w, h)
    ctx.set_source_rgba(*TILE_OUTLINE_COLOUR)
    ctx.stroke()


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

        draw_tile(self.context, MARGIN, MARGIN, w - 2*MARGIN, h - 2*MARGIN)
        #self.context.stroke()
        #self.context.rectangle(1, 1, w-2, h-2)
        #self.context.set_source_rgba(0, 0, 0, 1)
        #self.context.fill()

        self.context.set_source_rgba(1, 1, 1, 0.8)
        self.context.move_to(90, 140)
        #self.context.rotate(-0.5)
        self.context.set_font_size(32)
        self.context.show_text(u'HAPPY HOTDOG!')

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
