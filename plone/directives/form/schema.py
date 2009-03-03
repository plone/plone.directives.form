import sys
import os.path

import martian
import martian.error

import zope.interface

import plone.supermodel.model

import plone.supermodel
import plone.supermodel.utils

from zope.interface.interface import TAGGED_DATA

from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY, FIELDSETS_KEY
from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

TEMP_KEY = '__form_directive_values__'

# Base schemata

class Schema(zope.interface.Interface):
    """Base class for schema interfaces that can be grokked using the
    model() directive.
    """

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
        return [plone.supermodel.model.Fieldset(name, label=label, 
                    description=description, fields=fields)]

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

# Grokkers

class SupermodelSchemaGrokker(martian.InstanceGrokker):
    """Grok a schema that is to be loaded from a plone.supermodel XML file
    """
    martian.component(Schema.__class__)
    martian.directive(model)
    
    def execute(self, interface, config, **kw):
        
        if not interface.extends(Schema):
           return False
        
        filename = interface.queryTaggedValue(FILENAME_KEY, None)
        
        if filename is not None:
            
            schema = interface.queryTaggedValue(SCHEMA_NAME_KEY, u"")
            
            module_name = interface.__module__
            module = sys.modules[module_name]
        
            directory = module_name
        
            if hasattr(module, '__path__'):
                directory = module.__path__[0]
            elif "." in module_name:
                parent_module_name = module_name[:module_name.rfind('.')]
                directory = sys.modules[parent_module_name].__path__[0]
        
            directory = os.path.abspath(directory)
            filename = os.path.abspath(os.path.join(directory, filename))
            
            # Let / act as path separator on all platforms
            filename = filename.replace('/', os.path.sep)
        
            interface.setTaggedValue(FILENAME_KEY, filename)
        
            config.action(
                discriminator=('plone.supermodel.schema', interface, filename, schema),
                callable=scribble_schema,
                args=(interface,),
                order=9999,
                )
        
        return True

class FormSchemaGrokker(martian.InstanceGrokker):
    """Grok form schema hints
    """
    martian.component(Schema.__class__)
    
    martian.directive(fieldset)
    martian.directive(omitted)
    martian.directive(mode)
    martian.directive(widget)
    martian.directive(order_before)
    martian.directive(order_after)
    martian.directive(read_permission)
    martian.directive(write_permission)
    
    def execute(self, interface, config, **kw):
        
        if not interface.extends(Schema):
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

def scribble_schema(interface):
    
    filename = interface.getTaggedValue(FILENAME_KEY)
    schema = interface.queryTaggedValue(SCHEMA_NAME_KEY, u"")
    
    model = plone.supermodel.load_file(filename)
    
    if schema not in model.schemata:
        raise martian.error.GrokImportError(
                u"Schema '%s' specified for interface %s does not exist in %s." % 
                    (schema, interface.__identifier__, filename,)) 
    
    plone.supermodel.utils.sync_schema(model.schemata[schema], interface, overwrite=False)
    
__all__ = ('Schema', 'model', 'fieldset', 'omitted', 'mode', 'widget', 
            'order_before', 'order_after', 'read_permission', 'write_permission')