import martian
import five.grok

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
    """Marker base class for all grokked forms. Do not use directly.
    """
    martian.baseclass()
    
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
        changes = self.applyChanges(data)
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
        return zope.publisher.publish.mapply(self.render, (), self.request)
    render.base_method = True
        
__all__ = ('Form', 'SchemaForm', 'AddForm', 'SchemaAddForm', 
            'EditForm', 'SchemaEditForm', 'DisplayForm',)