import abc
import datetime
import six

class TimelineItem(object):
    """ Object used to describe an item on a timeline. """

    def __init__(self, id, start, end):
        """
        Constructs a TimelineItem.
        :param id: Some kind of unique identifier for the event.
        :param start: The start time (must be datetime).
        :param end: The end time (must be datetime).
        """
        assert(isinstance(start, datetime.datetime))
        assert(isinstance(end, datetime.datetime))

        self._id = id
        self._start = start
        self._end = end

    def id(self):
        return self._id

    def start(self):
        return self._start

    def end(self):
        return self._end


@six.add_metaclass(abc.ABCMeta)
class TimelinePlugin(object):
    """ An abstract base class for timeline augmentation. """

    @abc.abstractmethod
    def get_timeline_items(self, start, end):
        """
        Return a collection of TimelineItems relevant to the time frame.
        :param start: A datetime object (the start of the time frame).
        :param end: A datetime object (the end of the time frame).
        :return: A collection of TimelineItems.
        """
        pass

    def render_on_clockface(self, cairo_context, timeline_item, point_generator, line_generator):
        """
        Render the item on an arc.
        :param cairo_context: A cairo context object.
        :param timeline_item: The timeline item to render (as returned by the
        get_timeline_items function).
        :param point_generator: A callable that takes a time and returns the
        point on the clockface associated with that time.
        :param point_generator: A callable that takes a begin time and end time
        and and returns a collection of point representing the spiral on the
        clockface associated with that timespan.
        """
        pass



