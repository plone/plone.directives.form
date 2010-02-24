import sys

from zope.interface import implementer

from z3c.form.interfaces import IValidator
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators

class DecoratedValidator(SimpleFieldValidator):
    
    def __init__(self, fn, context, request, view, field, widget):
        super(DecoratedValidator, self).__init__(context, request, view, field, widget)
        self.fn = fn
    
    def validate(self, value):
        super(DecoratedValidator, self).validate(value)
        self.fn(value)

class validator(object):
    """Decorator for functions to be registered as validators
    """
    
    def __init__(self, **kw):
        self.discriminators = kw
    
    def __call__(self, fn):
        
        @implementer(IValidator)
        def factory(context, request, view, field, widget):
            return DecoratedValidator(fn, context, request, view, field, widget)
        
        WidgetValidatorDiscriminators(factory, **self.discriminators)
        
        frame = sys._getframe(1)
        adapters = frame.f_locals.get('__form_validator_adapters__', None)
        if adapters is None:
            frame.f_locals['__form_validator_adapters__'] = adapters = []
        adapters.append(factory)
        
        return fn

__all__ = ('validator',)
