import abc
import datetime
import six


@six.add_metaclass(abc.ABCMeta)
class TimelineItem(object):
    """ Object used to represent an item on a timeline. """

    def __init__(self):
        """
        Constructs a TimelineItem.
        """
        pass

    @abc.abstractmethod
    def id(self):
        pass

    @abc.abstractmethod
    def start(self):
        """ Return the start of the event (either a datetime or a date object). """
        pass

    @abc.abstractmethod
    def end(self):
        """ Return the start of the event (either a datetime or a date object). """
        pass

    @abc.abstractmethod
    def plugin(self):
        """ Return the plugin associated with this event. """
        pass

    @abc.abstractmethod
    def title(self):
        """ Return the title. """
        pass


@six.add_metaclass(abc.ABCMeta)
class Plugin(object):
    """ An abstract base class for a plugin. """

    @abc.abstractmethod
    def start(self):
        """ Start any active component within the plugin. """
        pass

    @abc.abstractmethod
    def stop(self):
        """ Stop any active component within the plugin. """
        pass

    @abc.abstractmethod
    def get_timeline_items(self, start, end):
        """
        Return a collection of TimelineItems relevant to the time frame.
        :param start: A datetime object (the start of the time frame).
        :param end: A datetime object (the end of the time frame).
        :return: A collection of TimelineItems.
        """
        pass

    @abc.abstractmethod
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



