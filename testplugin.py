import datetime

import cairocffi as cairo

import common
import timelineplugin

class TestPlugin(timelineplugin.TimelinePlugin):

    def get_timeline_items(self, start, end):

        now = datetime.datetime.now()
        return [timelineplugin.TimelineItem(
            id=0,
            start=now + datetime.timedelta(minutes=10),
            end=now + datetime.timedelta(minutes=30))]

    def render_on_clockface(self, cairo_context, timeline_item, arcs):
        for arc in arcs:
            assert(isinstance(arc, common.ArcParams))
            cairo_context.arc(*arc.centre, arc.radius, arc.start_angle, arc.end_angle)

            cairo_context.set_source_rgba(1,0,0,1)
            cairo_context.set_line_width(10)
            cairo_context.set_dash([],0)
            cairo_context.set_line_cap(cairo.constants.LINE_CAP_ROUND)

            cairo_context.stroke()
