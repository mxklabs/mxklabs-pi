import datetime

import cairocffi as cairo

import common
import timelineplugin

class TestPlugin(timelineplugin.TimelinePlugin):

    def get_timeline_items(self, start, end):

        now = datetime.datetime.now()
        return [timelineplugin.TimelineItem(
            id=0,
            start=now.replace(hour=20, minute=0, second=0, microsecond=0),
            end=now.replace(hour=21, minute=0, second=0, microsecond=0))]

    def render_on_clockface(self, cairo_context, timeline_item, point_generator, line_generator):

        points = line_generator(timeline_item.start(), timeline_item.end())

        assert(len(points)>=2)
        cairo_context.move_to(*points[0])
        for point in points[1:]:
            cairo_context.line_to(*point)

        #cairo_context.arc(*arc.centre, arc.radius, arc.start_angle, arc.end_angle)
        cairo_context.set_source_rgba(1,0,0,1)
        cairo_context.set_line_width(10)
        cairo_context.set_dash([],0)
        cairo_context.set_line_cap(cairo.constants.LINE_CAP_ROUND)
        cairo_context.stroke()
