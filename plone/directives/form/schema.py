import martian

from zope.interface import Interface
from zope.interface.interface import TAGGED_DATA

from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY, FIELDSETS_KEY
from plone.supermodel.model import Fieldset

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

TEMP_KEY = '__form_directive_values__'

# Base schemata

class Schema(Interface):
    """Base class for schema interfaces that can be grokked using the
    model() directive.
    """

# Storages

class FormMetadataDictStorage(object):
    """Store a dict value in the TEMP_KEY tagged value, under the key in
    directive.key
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(TAGGED_DATA, {}).setdefault(TEMP_KEY, {})
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
        tags = locals_.setdefault(TAGGED_DATA, {}).setdefault(TEMP_KEY, {})
        tags.setdefault(directive.key, []).extend(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(TEMP_KEY, {}).get(directive.key, default)

    def setattr(self, context, directive, value):
        tags = context.queryTaggedValue(TEMP_KEY, {})
        tags.setdefault(directive.key, []).extend(value)

class FilenameStorage(object):
    """Stores the model() directive value in a schema tagged value.
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(TAGGED_DATA, {})
        tags[FILENAME_KEY] = value["filename"]
        tags[SCHEMA_NAME_KEY] = value["schema"]

    def get(self, directive, component, default):
        return dict(filename=component.queryTaggedValue(FILENAME_KEY, default),
                    schema=component.queryTaggedValue(SCHEMA_NAME_KEY, default))

    def setattr(self, context, directive, value):
        context.setTaggedValue(FILENAME_KEY, value["filename"])
        context.setTaggedValue(SCHEMA_NAME_KEY, value["schema"])

class PrimaryFieldStorage(object):
    """Stores the primary() directive value in a schema tagged value.
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(TAGGED_DATA, {})
        tags.setdefault(directive.dotted_name(), []).extend(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(directive.dotted_name(), default)

    def setattr(self, context, directive, value):
        context.setTaggedValue(directive.dotted_name(), value)

# Directives

class model(martian.Directive):
    """Directive used to specify the XML model file
    """
    scope = martian.CLASS
    store = FilenameStorage()
    
    def factory(self, filename, schema=u""):
        return dict(filename=filename, schema=schema)

class fieldset(martian.Directive):
    """Directive used to create fieldsets
    """
    scope = martian.CLASS
    store = FormMetadataListStorage()
    
    key = FIELDSETS_KEY
    
    def factory(self, name, label=None, description=None, fields=None):
        return [Fieldset(name, label=label, description=description, fields=fields)]

class omitted(martian.Directive):
    """Directive used to omit one or more fields
    """
    
    scope = martian.CLASS
    store = FormMetadataDictStorage()
    
    key = OMITTED_KEY
    
    def factory(self, *args):
        return dict([(a, 'true') for a in args])

class mode(martian.Directive):
    """Directive used to set the mode of one or more fields
    """
    
    scope = martian.CLASS
    store = FormMetadataDictStorage()
    
    key = MODES_KEY
    
    def factory(self, **kw):
        return kw

class widget(martian.Directive):
    """Directive used to set the widget for one or more fields
    """
    
    scope = martian.CLASS
    store = FormMetadataDictStorage()
    
    key = WIDGETS_KEY
    
    def factory(self, **kw):
        widgets = {}
        for field_name, widget in kw.items():
            if not isinstance(widget, basestring):
                widget = "%s.%s" % (widget.__module__, widget.__name__)
            widgets[field_name] = widget
        return widgets
        
class order_before(martian.Directive):
    """Directive used to order one field before another
    """
    
    scope = martian.CLASS
    store = FormMetadataListStorage()
    
    key = ORDER_KEY
    
    def factory(self, **kw):
        return [(field_name, 'before', relative_to) for field_name, relative_to in kw.items()]

class order_after(martian.Directive):
    """Directive used to order one field after another
    """
    
    scope = martian.CLASS
    store = FormMetadataListStorage()
    
    key = ORDER_KEY
    
    def factory(self, **kw):
        return [(field_name, 'after', relative_to) for field_name, relative_to in kw.items()]

class read_permission(martian.Directive):
    """Directive used to set a field read permission
    """
    
    scope = martian.CLASS
    store = FormMetadataDictStorage()
    
    key = READ_PERMISSIONS_KEY
    
    def factory(self, **kw):
        return kw
        
class write_permission(martian.Directive):
    """Directive used to set a field write permission
    """
    
    scope = martian.CLASS
    store = FormMetadataDictStorage()
    
    key = WRITE_PERMISSIONS_KEY
    
    def factory(self, **kw):
        return kw

class primary(martian.Directive):
    """Directive used to mark one or more fields as 'primary'
    """
    
    scope = martian.CLASS
    store = PrimaryFieldStorage()
    
    def factory(self, *args):
        return args

__all__ = ('Schema', 'model', 'fieldset', 'omitted', 'mode', 'widget', 
            'order_before', 'order_after', 'read_permission',
            'write_permission', 'primary_field')