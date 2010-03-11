import martian
import five.grok

import grokcore.view.interfaces
import grokcore.view.util

import zope.component
import zope.interface

import z3c.form.form
import z3c.form.button

import plone.autoform.form
import plone.autoform.view

import zope.i18nmessageid

import zope.publisher.publish

from Products.statusmessages.interfaces import IStatusMessage

_ = zope.i18nmessageid.MessageFactory(u'plone.directives.form')

# Form base classes

class GrokkedForm(object):
    """Mixin class for all grokked forms, which provides grok.View-like
    semantics for template association, static resources, etc.
    
    Do not use directly.
    """
    martian.baseclass()
    
    # Emulate grokcore.view.View
    
    def __init__(self, context, request):
        super(GrokkedForm, self).__init__(context, request)
        
        # Set the view __name__
        self.__name__ = getattr(self, '__view_name__', None)
        
        # Set up the view.static resource directory reference
        if getattr(self, 'module_info', None) is not None:
            self.static = zope.component.queryAdapter(
                self.request,
                zope.interface.Interface,
                name=self.module_info.package_dotted_name
                )
        else:
            self.static = None
    
    def render(self):
        # Render a grok-style templat if we have one
        if (
            getattr(self, 'template') and
            grokcore.view.interfaces.ITemplate.providedBy(self.template)
        ):
            return self._render_template()
        else:
            return super(GrokkedForm, self).render()
    render.base_method = True
    
    @property
    def response(self):
        return self.request.response
    
    def _render_template(self):
        return self.template.render(self)

    def default_namespace(self):
        namespace = {}
        namespace['context'] = self.context
        namespace['request'] = self.request
        namespace['static'] = self.static
        namespace['view'] = self
        return namespace

    def namespace(self):
        return {}
    
    def url(self, obj=None, name=None, data=None):
        """Return string for the URL based on the obj and name. The data
        argument is used to form a CGI query string.
        """
        if isinstance(obj, basestring):
            if name is not None:
                raise TypeError(
                    'url() takes either obj argument, obj, string arguments, '
                    'or string argument')
            name = obj
            obj = None

        if name is None and obj is None:
            # create URL to view itself
            obj = self
        elif name is not None and obj is None:
            # create URL to view on context
            obj = self.context

        if data is None:
            data = {}
        else:
            if not isinstance(data, dict):
                raise TypeError('url() data argument must be a dict.')

        return grokcore.view.util.url(self.request, obj, name, data=data)

    def redirect(self, url):
        return self.request.response.redirect(url)
    
    # BBB: makes the form have the most important properties that were
    # exposed by the wrapper view
    
    @property
    def form_instance(self):
        return self
    
    @property
    def form(self):
        return self.__class__
    
# Page forms

class Form(GrokkedForm, z3c.form.form.Form):
    """A basic form.
    """
    martian.baseclass()

class SchemaForm(plone.autoform.form.AutoExtensibleForm, Form):
    """A basic extensible form
    """
    martian.baseclass()
    
    schema = None # Must be set by subclass

# Add forms

class AddForm(GrokkedForm, z3c.form.form.AddForm):
    """A standard add form.
    """
    martian.baseclass()
    
    immediate_view = None
    
    def __init__(self, context, request):
        super(AddForm, self).__init__(context, request)
        self.request['disable_border'] = True
    
    def render(self):
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ""
        return super(AddForm, self).render()
    
    def nextURL(self):
        if self.immediate_view is not None:
            return self.immediate_view
        else:
            return self.context.absolute_url()
    
    # Buttons
    
    @z3c.form.button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), "info")
    
    @z3c.form.button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Add New Item operation cancelled"), "info")
        self.request.response.redirect(self.nextURL()) 

    def updateActions(self):
        super(AddForm, self).updateActions()
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")

class SchemaAddForm(plone.autoform.form.AutoExtensibleForm, AddForm):
    """An extensible add form.
    """
    martian.baseclass()
    
    schema = None # Must be set by subclass

# Edit forms

class EditForm(GrokkedForm, z3c.form.form.EditForm):
    """A standard edit form
    """
    martian.baseclass()
    
    @z3c.form.button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), "info")
        self.request.response.redirect(self.context.absolute_url())
    
    @z3c.form.button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect(self.context.absolute_url()) 
    
    def updateActions(self):
        super(EditForm, self).updateActions()
        self.actions["save"].addClass("context")
        self.actions["cancel"].addClass("standalone")

class SchemaEditForm(plone.autoform.form.AutoExtensibleForm, EditForm):
    """An extensible edit form
    """
    martian.baseclass()
    
    schema = None # Must be set by subclass

# Display forms

class DisplayForm(plone.autoform.view.WidgetsView, five.grok.View):
    """A view that knows about field widgets, but otherwise has all the
    goodness of a grok.View, including automatic templates.
    """
    martian.baseclass()
    
    def __init__(self, context, request):
        plone.autoform.view.WidgetsView.__init__(self, context, request)
        five.grok.View.__init__(self, context, request)    
    
    def render(self):
        template = getattr(self, 'template', None)
        if template is not None:
            return self.template.render(self)
        return super(DisplayForm, self).render()
    render.base_method = True

# Directives

class wrap(martian.Directive):
    """Directive used on a form class to determine if a form wrapper view
    should be used.
    """
    scope = martian.CLASS
    store = martian.ONCE
    
    def factory(self, flag=True):
        return flag

__all__ = ('Form', 'SchemaForm', 'AddForm', 'SchemaAddForm', 
            'EditForm', 'SchemaEditForm', 'DisplayForm', 'wrap',)
