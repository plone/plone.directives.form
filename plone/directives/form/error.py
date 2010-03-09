import sys

from z3c.form.error import ComputedErrorViewMessage

class error_message(object):
    """Decorator for functions which may return an error message.
    
    The decorated function should take one argument, the value which caused
    the error, and return a message or unicode string::
    
        @form.error_message(error=TooSmall, field=IMySchema['myfield'])
        def myFieldTooSmall(value):
            return u"Please make %d bigger" % value
    """
    
    def __init__(self, **kw):
        self.discriminators = kw
    
    def __call__(self, fn):
        
        message = ComputedErrorViewMessage(fn, **self.discriminators)
        
        frame = sys._getframe(1)
        adapters = frame.f_locals.get('__form_error_message_adapters__', None)
        if adapters is None:
            frame.f_locals['__form_error_message_adapters__'] = adapters = []
        adapters.append(message)
        
        return fn

__all__ = ('error_message',)
