import argparse
import collections
import datetime
import math
import os
import time
import tkinter

import cairocffi as cairo
import PIL.Image
import PIL.ImageTk

from config import cfg

import common
import plugins.plugin

class CairoUtils(object):

    @staticmethod
    def set_fill_params(context, fill_params):
        """ Set context to fill_params. """
        context.set_source_rgba(*fill_params.colour)

    @staticmethod
    def draw_text(context, text, text_location, text_params):
        context.set_source_rgba(*text_params.colour)
        context.set_font_size(text_params.font_size)
        font_face = context.select_font_face(*text_params.font_face)
        context.set_font_face(font_face)
        _, _, _, h, _, _ = context.text_extents(text)
        new_text_location = (text_location[0], text_location[1] + text_params.height)

        with ContextRestorer(context):
            context.translate(*new_text_location)
            context.show_text(text)

        return new_text_location

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
    def line_to_points(context, points):
        for point in points:
            context.line_to(*point)

class ContextRestorer(object):

    def __init__(self, context):
        self._context = context
        self._matrix = None
        self._current_point = None

    def __enter__(self):
        self._matrix = self._context.get_matrix()
        if self._context.has_current_point():
            self._current_point = self._context.get_current_point()
        return None

    def __exit__(self, type, value, traceback):
        self._context.set_matrix(self._matrix)
        if self._current_point is not None:
            self._context.move_to(*self._current_point)

class AppHeading(object):

    def __init__(self, config):
        self._config = config
        self._bb = self._config.bounding_box

    def render(self, context, start_utc):
        text = self._config.text_fn()
        #context.set_source_rgba(*self._config.background)
        context.rectangle(float(self._bb.left), float(self._bb.top), float(self._bb.width), float(self._bb.height))
        CairoUtils.draw(context, self._config)

        text_location = CairoUtils.draw_text(context, text,
                                             (self._bb.left, self._bb.top),
                                             self._config.font)


class Clock(object):

    def __init__(self, config):
        self._config = config
        self._bb = self._config.bounding_box
        self._unit = self._bb.width

    def render(self, context, now):

        with ContextRestorer(context):

            # Translate to middle of clock face.
            context.translate(
                self._bb.left + self._bb.width / 2,
                self._bb.top + self._bb.height / 2)

            # Draw the face.
            context.arc(0, 0, self._unit / 2, 0, 2 * math.pi)
            CairoUtils.draw(context, self._config.face)

            # Draw ticks.
            for i in range(0, 60):

                if (i % 5) == 0:
                    tick_params = self._config.hour_ticks
                else:
                    tick_params = self._config.minute_ticks

                self.draw_tick(context, i, 60, tick_params)

            # Draw hour hand.
            self.draw_hand(context, now.hour * 60 + now.minute, 12 * 60, self._config.hour_hand)

            # Draw minute hand.
            self.draw_hand(context, now.minute, 60, self._config.minute_hand)

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

            p1 = (-(self._unit * params.back_thickness_pc) / 2,
                  +(self._unit * params.back_depth_pc))
            p2 = (+(self._unit * params.back_thickness_pc) / 2,
                  +(self._unit * params.back_depth_pc))
            p3 = (+(self._unit * params.front_thickness_pc) / 2,
                  -(self._unit * params.front_depth_pc))
            p4 = (-(self._unit * params.front_thickness_pc) / 2,
                  -(self._unit * params.front_depth_pc))

            context.line_to(*p1)
            context.line_to(*p2)
            context.line_to(*p3)
            context.line_to(*p4)
            context.line_to(*p1)

            CairoUtils.draw(context, params)

class Timeline(object):

    def __init__(self, config, plugins):
        self._config = config
        self._plugins = plugins
        self._bb = self._config.bounding_box
        self._unit = self._bb.width
        self._centre = (self._bb.left + self._bb.width / 2,
                        self._bb.top + self._bb.height / 2)
        self._events = None

    def set_timeline_events(self, events):
        self._events = events

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
        thickness = self._config.thickness

        start_angle = self.datetime_to_t(now)
        max_radius = (self._unit / 2) - offset

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

    def get_dt_control_points(self, start_utc, end_utc, hours):
        """
        Return a list of datetimes where the timespan in broken up in multiple
        of the parameters hours.
        """
        result = []

        # Find next
        floored_start_utc = start_utc.replace(hour=start_utc.hour//hours*hours, minute=0, second=0, microsecond=0)

        now_t = self.datetime_to_t(start_utc)
        i = 1

        while True:
            step = floored_start_utc + datetime.timedelta(hours=hours*i)
            if step > end_utc:
                break

            result += [step]

            i += 1

        return result

    def render(self, context, start_utc, end_utc):

        thickness = self._config.thickness
        length = self._config.length

        t_min = 0
        t_max = ((end_utc - start_utc).total_seconds() / (12 * 60 * 60)) * 2 * math.pi + 4 * math.pi

        #print("t_min={}".format(t_min))
        #print("t_max={}".format(t_max))

        separator_spiral_params = self.get_spiral_params(offset=0, now=start_utc)

        end_utc_plus = end_utc + datetime.timedelta(hours=12)

        control_points = [start_utc] + self.get_dt_control_points(
            start_utc, end_utc_plus, 12) + [end_utc_plus]

        for i in range(len(control_points)-1):
            dt_from = control_points[i]
            dt_to = control_points[i + 1]
            t_from = self.timedelta_to_t(dt_from - start_utc)
            t_to = self.timedelta_to_t(dt_to - start_utc)

            separator_spiral_points = self.get_spiral_points(separator_spiral_params, t_from, t_to)
            #print(separator_spiral_points)


            CairoUtils.line_to_points(context, separator_spiral_points)

            mid = dt_from + (dt_to - dt_from) / 2

            if mid.hour < 12:
                stroke = self._config.primary_stroke
            else:
                stroke = self._config.secondary_stroke

            #print(stroke.colour)
            #stroke.colour = stroke.colour[:3] + (stroke.colour[3] - i * 0.1,)

            CairoUtils.set_stroke_params(context, stroke)
            context.stroke()



        labels_spiral_params = self.get_spiral_params(offset=thickness/2, now=start_utc)

        # Find next
        floored_now = start_utc.replace(hour=start_utc.hour//3*3, minute=0, second=0, microsecond=0)

        context.set_font_size(10)

        now_t = self.datetime_to_t(start_utc)
        i = 1

        while True:

            label_datetime = floored_now + datetime.timedelta(hours=3*i)
            if label_datetime > end_utc:
                break

            label_secs = (label_datetime - start_utc).total_seconds()
            label_hours = 12 * int(label_secs // (12 * 60 * 60)) % (12 * 60 * 60)

            if label_hours > 0:
                label_text = "+{}h".format(label_hours)

                _, _, w, h, _, _ = context.text_extents(label_text)
                label_timedelta = label_datetime - start_utc
                label_t = self.timedelta_to_t(label_timedelta)

                label_point = self.get_spiral_point(labels_spiral_params, label_t)#

                with ContextRestorer(context):
                    #print(label_point)


                    #context.set_ctranslate(label_point[0], label_point[1])
                    context.translate(label_point[0], label_point[1])
                    #context.arc(0, 0, 10, 0, 2 * math.pi)


                    #context.rotate(now_t + label_t)
                    context.translate(-w / 2, h / 2)
                    context.move_to(0, 0)

                    #context.move_to(label_point[0] - w / 2,
                    #                label_point[1] + h / 2)

                    context.show_text(label_text)

            i += 1

        context.set_source_rgba(1, 0, 0, 1)
        context.stroke()

        for p in self._plugins: \

            assert (isinstance(p, plugins.plugin.Plugin))

            plugin_spiral_params = self.get_spiral_params(offset=thickness/2, now=start_utc)

            def spiral_point_generator(datetime):
                point_timedelta = datetime - start_utc
                point_t = self.timedelta_to_t(point_timedelta)

                return self.get_spiral_point(plugin_spiral_params, point_t)

            def spiral_points_generator(datetime_from, datetime_to):
                from_timedelta = datetime_from - start_utc
                from_t = self.timedelta_to_t(from_timedelta)
                to_timedelta = datetime_to - start_utc
                to_t = self.timedelta_to_t(to_timedelta)

                return self.get_spiral_points(plugin_spiral_params, from_t, to_t)

            for event in self._events:
                assert (isinstance(event, plugins.plugin.TimelineItem))
                if event.plugin() == p:
                    p.render_on_clockface(context, start_utc, end_utc, event,
                                          spiral_point_generator,
                                          spiral_points_generator)


class EventList(object):

    def __init__(self, config):
        self._config = config
        self._events = None

    def datetime_to_heading(self, dt_utc):
        """
        Workout what to display as a heading for a given datetime object with
        a UTC timezone. We basically translate the datetime to local time and
        if it matches today's date, we call 'today_header_text_fn', for tomorrow's
        date we call 'tomorrow_header_text_fn' and otherwise we call
        'datetime_header_text_fn' with the event's date.
        """
        now_utc = datetime.datetime.utcnow()
        now_local = common.utc_to_local(now_utc)
        tomorrow_local = common.utc_to_local(now_utc + datetime.timedelta(days=1))
        dt_local = common.utc_to_local(dt_utc)

        if now_local.year == dt_local.year and \
                now_local.month == dt_local.month and \
                now_local.day == dt_local.day:
            return self._config.today_header_text_fn()
        elif tomorrow_local.year == dt_local.year and \
                tomorrow_local.month == dt_local.month and \
                tomorrow_local.day == dt_local.day:
            return self._config.tomorrow_header_text_fn()
        else:
            return self._config.datetime_header_text_fn(dt_local)

    def render(self, context):


        text_location = (self._config.bounding_box.left, self._config.bounding_box.top)


        day = None

        for event in self._events:
            event_day = event.start().replace(hour=0, minute=0, second=0, microsecond=0)



            if event_day != day:
                text = self.datetime_to_heading(event.start())
                text_location = CairoUtils.draw_text(context, text,
                                                     text_location, self._config.heading.font)
                day = event_day


            text_location = CairoUtils.draw_text(context,
                                                 event.title(),
                                                 text_location,
                                                 self._config.event.font)


    def set_timeline_events(self, events):
        self._events = events


class MainWindow(tkinter.Tk):

    def __init__(self, config, debug, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._config = config

        if not debug:
            super().attributes("-fullscreen", True)
            super().config(cursor="none")


        self.size = config.window.width, config.window.height
        self.geometry("{}x{}".format(*self.size))
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *self.size)
        self.context = cairo.Context(self.surface)

        self._plugins = [plugin.plugin(plugin.config) for plugin in
                         config.plugins]
        self._timeline = Timeline(self._config.timeline, self._plugins)
        self._event_list = EventList(config.event_list)
        self._app_heading = AppHeading(self._config.app_heading)
        self._clock = Clock(self._config.clock)

        self.label = tkinter.Label(self)
        self.label.pack(expand=True, fill="both")


        for p in self._plugins:
            p.start()

        try:
            while True:
                events = []

                now = datetime.datetime.now()

                for p in self._plugins:
                    events += p.get_timeline_items(now, now + self._config.timespan)

                events.sort(key=lambda e: e.start())

                self._event_list.set_timeline_events(events)
                self._timeline.set_timeline_events(events)

                self.render(now)
                self.update_idletasks()
                self.update()



                time.sleep(5)

        except KeyboardInterrupt:
            print("")
            print("Stopping all plugins.")
            for p in self._plugins:
                p.stop()
            print("Exiting.")


    def render(self, now):


        self.context.set_operator(cairo.constants.OPERATOR_OVER)

        self.context.rectangle(0, 0, *self.size)
        self.context.set_source_rgba(*self._config.window.background_colour)
        self.context.fill()

        #self.context.set_operator(cairo.constants.OPERATOR_SCREEN)

        self._timeline.render(self.context, now, now + self._config.timespan)
        self._clock.render(self.context, now)
        self._event_list.render(self.context)
        self._app_heading.render(self.context, now)

        new_img = PIL.Image.frombuffer("RGBA", self.size,
                                   self.surface.get_data(),
                                   "raw","BGRA", 0, 1)
        new_tk_img = PIL.ImageTk.PhotoImage(new_img)

        self.label.configure(image=new_tk_img)
        self.label.image = new_tk_img
        #panel.image = img2




if __name__ == "__main__":
    """
    Using the argparse module to ease the development process of this source
    code a little. Start this file with command-line argument '--mode debug' to
    avoid going in fullscreen mode and to avoid hiding the cursor.
    """

    # Set current directory to main.py's directory.
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Proccess command-line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['release', 'debug', 'auth'], default='release')
    args = parser.parse_args()

    if args.mode == 'auth':
        for plugin in cfg.plugins:
            p = plugin.plugin(plugin.config)
            if hasattr(p, 'auth'):
                p.authenticate()
    else:
        MainWindow(config=cfg, debug=(args.mode == 'debug'))
