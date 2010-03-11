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

from plone.autoform.interfaces import (
        OMITTED_KEY,
        READ_PERMISSIONS_KEY,
        WRITE_PERMISSIONS_KEY,
        WIDGETS_KEY,
        MODES_KEY,
        ORDER_KEY,
    )

from plone.directives.form.form import (
        GrokkedForm,
        Form,
        EditForm,
        SchemaEditForm,
        AddForm,
        SchemaAddForm,
        DisplayForm,
        wrap,
    )

from plone.directives.form.schema import (
        Schema,
        model,
        fieldset,
        omitted,
        no_omit,
        mode,
        widget,
        order_before,
        order_after,
        read_permission,
        write_permission,
        primary,
        TEMP_KEY,
    )

# Whether or not we need to wrap the grokked form using the layout form
# wrapper. We do this by default in Zope < 2.12, but not in Zope 2.12+, where
# it is unnecessary.
DEFAULT_WRAP = True
try:
    import pkg_resources
    zope2Version = pkg_resources.get_distribution('Zope2').version.split('.')
    if int(zope2Version[0]) > 2 or (int(zope2Version[0]) == 2 and int(zope2Version[1]) >= 12):
        DEFAULT_WRAP = False
except:
    pass

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
    martian.directive(wrap, default=None)
    
    default_permissions = {
        EditForm          : 'cmf.ModifyPortalContent',
        SchemaEditForm    : 'cmf.ModifyPortalContent',
        AddForm           : 'cmf.AddPortalContent',
        SchemaAddForm     : 'cmf.AddPortalContent',
    }
    
    permission_fallback = 'zope2.View'
    
    def grok(self, name, form, module_info, **kw):
        # save the module info so that we can look for templates later
        form.module_info = module_info
        return super(FormGrokker, self).grok(name, form, module_info, **kw)
    
    def execute(self, form, config, context, layer, name, permission, wrap, **kw):
        
        if permission is None:
            permission = self.default_permissions.get(form.__class__, self.permission_fallback)

        if issubclass(form, AutoExtensibleForm):
            if getattr(form, 'schema', None) is None:
                
                if issubclass(form, (EditForm, Form)) and IInterface.providedBy(context):
                    form.schema = context
                else:
                    raise GrokImportError(
                        u"The schema form %s must have a 'schema' attribute "
                          "defining a schema interface for the form. If you want "
                          "to set up your fields manually, use a non-schema form "
                          "base class instead." % (form.__name__))
        
        templates = form.module_info.getAnnotation('grok.templates', None)
        if templates is not None:
            config.action(
                discriminator=None,
                callable=self.checkTemplates,
                args=(templates, form.module_info, form)
                )
        
        form.__view_name__ = name
        
        if wrap is None:
            wrap = DEFAULT_WRAP
        
        # Only use the wrapper view if we are on Zope < 2.12
        if wrap:
            factory = wrap_form(form)
            factory.__view_name__ = name
        else:
            factory = form
        
        page_directive(
                config,
                name=name,
                permission=permission,
                for_=context,
                layer=layer,
                class_=factory
            )
        
        return True
    
    def checkTemplates(self, templates, module_info, factory):
        
        def has_render(factory):
            render = getattr(factory, 'render', None)
            base_method = getattr(render, 'base_method', False)
            return render and not base_method
        
        def has_no_render(factory):
            # Unlike the view grokker, we are happy with the base class
            # version
            return getattr(factory, 'render', None) is None
        
        templates.checkTemplates(module_info, factory, 'view',
                                 has_render, has_no_render)

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
    martian.directive(no_omit)
    martian.directive(mode)
    martian.directive(widget)
    martian.directive(order_before)
    martian.directive(order_after)
    martian.directive(read_permission)
    martian.directive(write_permission)
    martian.directive(primary)
    
    def execute(self, interface, config, **kw):
        
        directiveSupplied = interface.queryTaggedValue(TEMP_KEY, None)
        primaryFields = interface.queryTaggedValue(primary.dotted_name(), [])
        
        if not interface.extends(Schema):
            if directiveSupplied or primaryFields:
                raise GrokImportError(
                        u"You have used plone.directives.form directives "
                        u"on the interface %s, but this does not derive from "
                        u"plone.directives.form.Schema." % (interface.__identifier__,)
                    )
            return False
        
        # Copy from temporary to real value
        if directiveSupplied is not None:
            for key, tgv in directiveSupplied.items():
                existingValue = interface.queryTaggedValue(key, None)
                
                # Validate that the value refers to something actually in 
                # the interface
                
                fieldNamesToCheck = []
                
                if key in (WIDGETS_KEY, READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY):
                    fieldNamesToCheck = tgv.keys()
                elif key in (ORDER_KEY,):
                    fieldNamesToCheck = [t[0] for t in tgv]
                elif key in (OMITTED_KEY, MODES_KEY):
                    fieldNamesToCheck = [t[1] for t in tgv]
                
                for fieldName in fieldNamesToCheck:
                    if fieldName not in interface:
                        raise GrokImportError(
                                u"The directive %s applied to interface %s "
                                u"refers to unknown field name %s" % (key, interface.__identifier__, fieldName)
                            )
                
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
        
        for fieldName in primaryFields:
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

# Value adapter grokker

class ValueAdapterGrokker(martian.GlobalGrokker):
    
    def grok(self, name, module, module_info, config, **kw):
        # context = grokcore.component.context.bind().get(module=module)
        adapters = module_info.getAnnotation('form.value_adapters', [])
        for factory, name in adapters:
            adapter_directive(config,
                factory=(factory,),
                name=name
            )
        return True

# Validator adapter grokker

class ValidatorAdapterGrokker(martian.GlobalGrokker):
    
    def grok(self, name, module, module_info, config, **kw):
        # context = grokcore.component.context.bind().get(module=module)
        adapters = module_info.getAnnotation('form.validator_adapters', [])
        for factory in adapters:
            adapter_directive(config,
                factory=(factory,),
            )
        return True

# Error message adapter grokker

class ErrorMessageAdapterGrokker(martian.GlobalGrokker):
    
    def grok(self, name, module, module_info, config, **kw):
        # context = grokcore.component.context.bind().get(module=module)
        adapters = module_info.getAnnotation('form.error_message_adapters', [])
        for factory in adapters:
            adapter_directive(config,
                factory=(factory,),
                name=u"message",
            )
        return True
