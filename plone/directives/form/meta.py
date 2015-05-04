from zope.interface.interfaces import IInterface

import martian
import grokcore.component
import grokcore.view
import grokcore.view.meta.views

from martian.error import GrokImportError

from plone.autoform.form import AutoExtensibleForm
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.z3cform.layout import wrap_form

from Products.Five.browser.metaconfigure import page as page_directive
from zope.component.zcml import adapter as adapter_directive

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


class FormTemplateGrokker(grokcore.view.meta.views.TemplateGrokker):
    martian.component(GrokkedForm)

    def has_no_render(self, factory):
        # Unlike the view template grokker, we are happy with the base class
        # version
        return getattr(factory, 'render', None) is None


class FormGrokker(martian.ClassGrokker):
    """Wrap standard z3c.form forms with plone.z3cform.layout and register
    them as views, using the same directives as other views. Note that
    templates are *not* automatically assigned.
    """

    martian.component(GrokkedForm)

    martian.directive(grokcore.component.context)
    martian.directive(grokcore.view.layer, default=IDefaultBrowserLayer)
    martian.directive(grokcore.component.name, get_default=default_view_name)
    martian.directive(
        grokcore.security.require,
        name='permission',
        default=None)
    martian.directive(wrap, default=None)

    default_permissions = {
        EditForm: 'cmf.ModifyPortalContent',
        SchemaEditForm: 'cmf.ModifyPortalContent',
        AddForm: 'cmf.AddPortalContent',
        SchemaAddForm: 'cmf.AddPortalContent',
    }

    permission_fallback = 'zope2.View'

    def grok(self, name, form, module_info, **kw):
        # save the module info so that we can look for templates later
        form.module_info = module_info
        return super(FormGrokker, self).grok(name, form, module_info, **kw)

    def execute(
            self, form, config, context, layer, name, permission, wrap, **kw):

        if permission is None:
            permission = self.default_permissions.get(
                form.__class__,
                self.permission_fallback)

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
