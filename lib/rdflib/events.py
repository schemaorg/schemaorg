__doc__ = """
Dirt Simple Events

A Dispatcher (or a subclass of Dispatcher) stores event handlers that
are 'fired' simple event objects when interesting things happen.

Create a dispatcher:

  >>> d = Dispatcher()

Now create a handler for the event and subscribe it to the dispatcher
to handle Event events.  A handler is a simple function or method that
accepts the event as an argument:

  >>> def handler1(event): print(repr(event))
  >>> d.subscribe(Event, handler1)

Now dispatch a new event into the dispatcher, and see handler1 get
fired:

  >>> d.dispatch(Event(foo='bar', data='yours', used_by='the event handlers'))
  <rdflib.events.Event ['data', 'foo', 'used_by']>
"""

__all__ = ['Event', 'Dispatcher']


class Event(object):
    """
    An event is a container for attributes.  The source of an event
    creates this object, or a subclass, gives it any kind of data that
    the events handlers need to handle the event, and then calls
    notify(event).

    The target of an event registers a function to handle the event it
    is interested with subscribe().  When a sources calls
    notify(event), each subscriber to that event will be called in no
    particular order.
    """

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self):
        attrs = self.__dict__.keys()
        attrs.sort()
        return '<rdflib.events.Event %s>' % ([a for a in attrs],)


class Dispatcher(object):
    """
    An object that can dispatch events to a privately managed group of
    subscribers.
    """

    _dispatch_map = None

    def set_map(self, amap):
        self._dispatch_map = amap

    def get_map(self):
        return self._dispatch_map

    def subscribe(self, event_type, handler):
        """ Subscribe the given handler to an event_type.  Handlers
        are called in the order they are subscribed.
        """
        if self._dispatch_map is None:
            self.set_map({})
        lst = self._dispatch_map.get(event_type, None)
        if lst is None:
            lst = [handler]
        else:
            lst.append(handler)
        self._dispatch_map[event_type] = lst

    def dispatch(self, event):
        """ Dispatch the given event to the subscribed handlers for
        the event's type"""
        if self._dispatch_map is not None:
            lst = self._dispatch_map.get(type(event), None)
            if lst is None:
                raise ValueError("unknown event type: %s" % type(event))
            for l in lst:
                l(event)


def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
