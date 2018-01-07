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

import cairocffi as cairo
from PIL import Image, ImageTk

from config import cfg
import plugins.plugin

BoundingBox = collections.namedtuple("BoundingBox", ["left","top","width",
    "height"])

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
        if params.fill and params.stroke:
            CairoUtils.set_fill_params(context, params.fill)
            context.fill_preserve()
            CairoUtils.set_stroke_params(context, params.stroke)
            context.stroke()
        elif params.fill:
            CairoUtils.set_fill_params(context, params.fill)
            context.fill()
        elif params.stroke:
            CairoUtils.set_stroke_params(context, params.stroke)
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

    @staticmethod
    def move_to_points(context, points):
        for point in points:
            context.line_to(*point)

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

    def __init__(self, bounding_box):
        margin_bb = CairoUtils.get_margin_box(
            bounding_box=bounding_box,
            margin=cfg.clock.margin)
        self._real_bb = CairoUtils.get_square_box(margin_bb)
        self._unit = self._real_bb.width

    def render(self, context, now):

        with ContextRestorer(context):

            # Translate to middle of clock face.
            context.translate(
                self._real_bb.left + self._real_bb.width / 2,
                self._real_bb.top + self._real_bb.height / 2)

            # Draw ticks.
            for i in range(0, 60):

                if (i % 5) == 0:
                    tick_params = cfg.clock.hour_ticks
                else:
                    tick_params = cfg.clock.minute_ticks

                self.draw_tick(context, i, 60, tick_params)

            # Draw hour hand.
            self.draw_hand(context, now.hour * 60 + now.minute, 12 * 60, cfg.clock.hour_hand)

            # Draw minute hand.
            self.draw_hand(context, now.minute, 60, cfg.clock.minute_hand)

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
                -(self._unit * params.thickness_pc) / 2,
                -(self._unit * params.front_depth_pc),
                 (self._unit * params.thickness_pc),
                 (self._unit * (params.front_depth_pc
                    + params.back_depth_pc)))

            CairoUtils.draw(context, params)

class Timeline(object):

    def __init__(self, bounding_box, plugins):
        self._plugins = plugins
        self._bb = CairoUtils.get_square_box(
            CairoUtils.get_margin_box(
                bounding_box=bounding_box,
                margin=cfg.timeline.margin))
        self._unit = self._bb.width
        self._centre = (self._bb.left + self._bb.width / 2,
                        self._bb.top + self._bb.height / 2)

    def datetime_to_t(self, datetime):
        return 2 * math.pi * (datetime.hour * 60 + datetime.minute) / (12 * 60)

    def timedelta_to_t(self, timedelta):
        return 2*math.pi*timedelta.total_seconds() / (12 * 60 * 60)

    def get_spiral_params(self, offset, now):
        """
        Calculate the parameters a,b to the spiral described by
            x = (a * t + b) * math.sin(c * t + d)
            y = (a * t + b) * math.cos(c * t + d)
        where t=0 is closest to the edge of the clock face and every increment
        of 2*math.pi corresponds to one rotation of the clock face.
        """
        margin = cfg.timeline.margin
        thickness = cfg.timeline.thickness

        start_angle = self.datetime_to_t(now)
        max_radius = (self._unit / 2) - margin - offset

        # Parameter 'a' corresponds to minus one 'thickness' per rotation.
        a = -thickness / (2 * math.pi)
        b = max_radius
        c = -1.0
        d = math.pi - start_angle

        return (a, b, c, d)

    def get_spiral_point(self, spiral_params, t):
        scalar = spiral_params[0] * t + spiral_params[1]
        angle = spiral_params[2] * t + spiral_params[3]
        x = scalar * math.sin(angle)
        y = scalar * math.cos(angle)

        return (self._centre[0] + x, self._centre[1] + y)

    def get_spiral_points(self, spiral_params, t_min, t_max):
        result = []
        t = t_min
        while t < t_max:
            point = self.get_spiral_point(spiral_params, t)
            result.append(point)
            t += 0.1

        point = self.get_spiral_point(spiral_params, t_max)
        result.append(point)

        if len(result) == 1:
            result.append(result[0])

        return result

    def render(self, context, now):

        #context.translate(*self._centre)
        thickness = cfg.timeline.thickness
        length = cfg.timeline.length

        t_min = 0
        t_max = (length.total_seconds() / (12 * 60 * 60)) * 2 * math.pi

        #print("t_min={}".format(t_min))
        #print("t_max={}".format(t_max))

        separator_spiral_params = self.get_spiral_params(offset=thickness, now=now)
        separator_spiral_points = self.get_spiral_points(separator_spiral_params, t_min, t_max)
        CairoUtils.move_to_points(context, separator_spiral_points)
        CairoUtils.set_stroke_params(context, cfg.timeline.stroke)
        context.stroke()

        labels_spiral_params = self.get_spiral_params(offset=thickness/2, now=now)

        # Find next
        floored_now = now.replace(hour=now.hour//3*3, minute=0, second=0, microsecond=0)
        print("floored_now={}".format(floored_now))

        context.set_font_size(10)

        now_t = self.datetime_to_t(now)
        i = 1

        while True:

            label_datetime = floored_now + datetime.timedelta(hours=3*i)
            if label_datetime > now + length:
                break

            label_secs = (label_datetime - now).total_seconds()
            label_hours = 12 * int(label_secs // (12 * 60 * 60)) % (12 * 60 * 60)

            if label_hours > 0:
                label_text = "+{}h".format(label_hours)

                _, _, w, h, _, _ = context.text_extents(label_text)
                label_timedelta = label_datetime - now
                label_t = self.timedelta_to_t(label_timedelta)
                label_point = self.get_spiral_point(labels_spiral_params, label_t)#

                with ContextRestorer(context):
                    context.translate(label_point[0], label_point[1])
                    context.rotate(now_t + label_t)
                    context.move_to(-w/2, h/2)
                    context.show_text(label_text)

            i += 1

        for p in self._plugins: \

            assert (isinstance(p, plugins.plugin.Plugin))

            plugin_spiral_params = self.get_spiral_params(offset=thickness/2, now=now)

            def spiral_point_generator(datetime):
                point_timedelta = datetime - now
                point_t = self.timedelta_to_t(point_timedelta)

                return self.get_spiral_point(plugin_spiral_params, point_t)

            def spiral_points_generator(datetime_from, datetime_to):
                from_timedelta = datetime_from - now
                from_t = self.timedelta_to_t(from_timedelta)
                to_timedelta = datetime_to - now
                to_t = self.timedelta_to_t(to_timedelta)

                return self.get_spiral_points(plugin_spiral_params, from_t, to_t)

            timeline_items = p.get_timeline_items(now, now + cfg.timeline.length)

            for timeline_item in timeline_items:
                assert(isinstance(timeline_item, plugins.plugin.TimelineItem))
                p.render_on_clockface(context, timeline_item, spiral_point_generator, spiral_points_generator)


class ExampleGui(Tk):
    def __init__(self, debug, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self._plugins = [plugin.type(plugin.config) for plugin in cfg.plugins]

        if not debug:
            super().attributes("-fullscreen", True)
            super().config(cursor="none")

        self.size = cfg.window.width, cfg.window.height

        self.geometry("{}x{}".format(*self.size))

        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.size)
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



        self._timeline = Timeline(bounding_box, self._plugins)
        self._clock = Clock(bounding_box)
        
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

        now = datetime.datetime.now()

        self.context.set_operator(cairo.constants.OPERATOR_OVER)

        self.context.rectangle(0, 0, *self.size)
        self.context.set_source_rgba(*cfg.window.background_colour)
        self.context.fill()

        #self.context.set_operator(cairo.constants.OPERATOR_SCREEN)

        self._clock.render(self.context, now)
        self._timeline.render(self.context, now)

        new_img = Image.frombuffer("RGBA", self.size,
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
