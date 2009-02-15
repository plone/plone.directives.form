import zope.interface
import zope.component

import zope.interface.interface

import martian

import plone.directives.form.schema

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

TEMP_KEY = '__form_directive_values__'

# Storages

class FormMetadataDictStorage(object):
    """Store a dict value in the TEMP_KEY tagged value, under the key in
    directive.key
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(zope.interface.interface.TAGGED_DATA, {}).setdefault(TEMP_KEY, {})
        tags.setdefault(directive.key, {}).update(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(TEMP_KEY, {}).get(directive.key, default)

    def setattr(self, context, directive, value):
        tags = context.queryTaggedValue(TEMP_KEY, {})
        tags.setdefault(directive.key, {}).update(value)

class FormMetadataListStorage(object):
    """Store a list value in the TEMP_KEY tagged value, under the key in
    directive.key
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(zope.interface.interface.TAGGED_DATA, {}).setdefault(TEMP_KEY, {})
        tags.setdefault(directive.key, []).extend(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(TEMP_KEY, {}).get(directive.key, default)

    def setattr(self, context, directive, value):
        tags = context.queryTaggedValue(TEMP_KEY, {})
        tags.setdefault(directive.key, []).extend(value)

FORM_METADATA_DICT = FormMetadataDictStorage()        
FORM_METADATA_LIST = FormMetadataListStorage()

# Directives

class omitted(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA_DICT
    
    key = OMITTED_KEY
    
    def factory(self, *args):
        return dict([(a, 'true') for a in args])

class mode(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA_DICT
    
    key = MODES_KEY
    
    def factory(self, **kw):
        return kw

class widget(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA_DICT
    
    key = WIDGETS_KEY
    
    def factory(self, **kw):
        widgets = {}
        for field_name, widget in kw.items():
            if not isinstance(widget, basestring):
                widget = "%s.%s" % (widget.__module__, widget.__name__)
            widgets[field_name] = widget
        return widgets
        
class order_before(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA_LIST
    
    key = ORDER_KEY
    
    def factory(self, **kw):
        return [(field_name, 'before', relative_to) for field_name, relative_to in kw.items()]

class order_after(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA_LIST
    
    key = ORDER_KEY
    
    def factory(self, **kw):
        return [(field_name, 'after', relative_to) for field_name, relative_to in kw.items()]

class read_permission(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA_DICT
    
    key = READ_PERMISSIONS_KEY
    
    def factory(self, **kw):
        return kw
        
class write_permission(martian.Directive):
    
    scope = martian.CLASS
    store = FORM_METADATA_DICT
    
    key = WRITE_PERMISSIONS_KEY
    
    def factory(self, **kw):
        return kw

# Grokkers

class FormSchemaGrokker(martian.InstanceGrokker):
    martian.component(plone.directives.form.schema.Schema.__class__)
    
    martian.directive(omitted)
    martian.directive(mode)
    martian.directive(widget)
    martian.directive(order_before)
    martian.directive(order_after)
    martian.directive(read_permission)
    martian.directive(write_permission)
    
    def execute(self, interface, config, **kw):
        
        if not interface.extends(plone.directives.form.schema.Schema):
            return False
            
        # Copy from temporary to real value
        directive_supplied = interface.queryTaggedValue(TEMP_KEY, None)
        if directive_supplied is None:
            return False
        
        for key, tgv in directive_supplied.items():
            existing_value = interface.queryTaggedValue(key, None)
            
            if existing_value is not None:
                if type(existing_value) != type(tgv):
                    # Don't overwrite if we have a different type
                    continue
                elif isinstance(existing_value, list):
                    existing_value.extend(tgv)
                    tgv = existing_value
                elif isinstance(existing_value, dict):
                    existing_value.update(tgv)
                    tgv = existing_value
                    
            interface.setTaggedValue(key, tgv)
        
        interface.setTaggedValue(TEMP_KEY, None)
        return True

__all__ = ('omitted', 'mode', 'widget', 'order_before', 'order_after')