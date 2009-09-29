import sys
import os.path

from zope.interface.interfaces import IInterface
from zope.interface import alsoProvides

import martian
import grokcore.component
import grokcore.view

from martian.error import GrokImportError

from plone.autoform.form import AutoExtensibleForm
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.z3cform.layout import wrap_form

from Products.Five.browser.metaconfigure import page as page_directive
from zope.component.zcml import adapter as adapter_directive

from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY
from plone.supermodel.utils import syncSchema
from plone.supermodel import loadFile

from plone.rfc822.interfaces import IPrimaryField

from plone.directives.form.form import (
        GrokkedForm,
        Form,
        EditForm,
        SchemaEditForm,
        AddForm,
        SchemaAddForm,
        DisplayForm,
    )
    
from plone.directives.form.schema import (
        Schema,
        model,
        fieldset,
        omitted,
        mode,
        widget,
        order_before,
        order_after,
        read_permission,
        write_permission,
        primary,
        TEMP_KEY,
    )

# Form grokkers

def default_view_name(factory, module=None, **data):
    return factory.__name__.lower()

class FormGrokker(martian.ClassGrokker):
    """Wrap standard z3c.form forms with plone.z3cform.layout and register
    them as views, using the same directives as other views. Note that
    templates are *not* automatically assigned.
    """
    
    martian.component(GrokkedForm)
    
    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(grokcore.security.require, name='permission', default=None)
    
    default_permissions = {
        EditForm          : 'cmf.ModifyPortalContent',
        SchemaEditForm    : 'cmf.ModifyPortalContent',
        AddForm           : 'cmf.AddPortalContent',
        SchemaAddForm     : 'cmf.AddPortalContent',
    }
    
    permission_fallback = 'zope.Public'

    def execute(self, form, config, context, layer, name, permission, **kw):
        
        if permission is None:
            permission = self.default_permissions.get(form.__class__, self.permission_fallback)

        if issubclass(form, AutoExtensibleForm):
            if getattr(form, 'schema', None) is None:
                
                if issubclass(form, (EditForm, Form)) and \
                        IInterface.providedBy(context):
                    form.schema = context
                else:
                    raise GrokImportError(
                        u"The schema form %s must have a 'schema' attribute "
                          "defining a schema interface for the form. If you want "
                          "to set up your fields manually, use a non-schema form "
                          "base class instead." % (form.__name__))
        
        factory = wrap_form(form)
        form.__view_name__ = factory.__view_name__ = name
        form.__name__ = factory.__name__ = name
        
        page_directive(
                config,
                name=name,
                permission=permission,
                for_=context,
                layer=layer,
                class_=factory
            )

        return True

class DisplayFormGrokker(martian.ClassGrokker):
    """Let a display form use its context as an implicit schema, if the
    context has been set.
    """
    
    martian.component(DisplayForm)
    
    martian.directive(grokcore.component.context)

    def execute(self, factory, config, context, **kw):
        
        if getattr(factory, 'schema', None) is None and \
                IInterface.providedBy(context):
            factory.schema = context
            return True
        else:
            return False
            
# Schema grokkers

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
            
            moduleName = interface.__module__
            module = sys.modules[moduleName]
        
            directory = moduleName
        
            if hasattr(module, '__path__'):
                directory = module.__path__[0]
            elif "." in moduleName:
                parentModuleName = moduleName[:moduleName.rfind('.')]
                directory = sys.modules[parentModuleName].__path__[0]
        
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
    martian.directive(primary)
    
    def execute(self, interface, config, **kw):
        
        if not interface.extends(Schema):
            return False
            
        # Copy from temporary to real value
        directiveSupplied = interface.queryTaggedValue(TEMP_KEY, None)
        if directiveSupplied is not None:
            for key, tgv in directiveSupplied.items():
                existingValue = interface.queryTaggedValue(key, None)
            
                if existingValue is not None:
                    if type(existingValue) != type(tgv):
                        # Don't overwrite if we have a different type
                        continue
                    elif isinstance(existingValue, list):
                        existingValue.extend(tgv)
                        tgv = existingValue
                    elif isinstance(existingValue, dict):
                        existingValue.update(tgv)
                        tgv = existingValue
                    
                interface.setTaggedValue(key, tgv)
        
            interface.setTaggedValue(TEMP_KEY, None)
        
        for fieldName in interface.queryTaggedValue(primary.dotted_name(), []):
            try:
                alsoProvides(interface[fieldName], IPrimaryField)
            except KeyError:
                raise GrokImportError("Field %s set in primary() directive on %s not found" % (fieldName, interface,))
        
        return True

def scribble_schema(interface):
    
    filename = interface.getTaggedValue(FILENAME_KEY)
    schema = interface.queryTaggedValue(SCHEMA_NAME_KEY, u"")
    
    model = loadFile(filename)
    
    if schema not in model.schemata:
        raise GrokImportError(
                u"Schema '%s' specified for interface %s does not exist in %s." % 
                    (schema, interface.__identifier__, filename,)) 
    
    syncSchema(model.schemata[schema], interface, overwrite=False)

# Value adapter grokkers

class ValueAdapterGrokker(martian.GlobalGrokker):

    def grok(self, name, module, module_info, config, **kw):
        context = grokcore.component.context.bind().get(module=module)
        adapters = module_info.getAnnotation('form.value_adapters', [])
        for factory, name in adapters:
            adapter_directive(config,
                factory=(factory,),
                name=name
            )
        return True
