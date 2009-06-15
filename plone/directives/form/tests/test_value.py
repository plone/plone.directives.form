import unittest

import zope.component.testing

from zope.interface import implements, Interface
from zope import schema

from grokcore.component.testing import grok

from z3c.form.form import EditForm, AddForm
from z3c.form.field import Fields

from z3c.form.testing import setupFormDefaults, TestRequest

from plone.directives import form

class IFolder(Interface):
    pass

class IDummySchema(Interface):
    
    field1 = schema.TextLine(title=u"Field one")
    field2 = schema.TextLine(title=u"Field two")

class Folder(object):
    implements(IFolder)

class Dummy(object):
    implements(IDummySchema)
    
    field1 = u"Field 1 default"
    field2 = u""

class DummyEditForm(EditForm):
    
    fields = Fields(IDummySchema)

class DummyAddForm(AddForm):
    
    fields = Fields(IDummySchema)

class DummySecondaryAddForm(AddForm):
    
    fields = Fields(IDummySchema)
    
@form.default_value(field=IDummySchema['field1'])
def field1_default(data):
    return u"A dummy"

@form.default_value(field=IDummySchema['field1'], form=DummySecondaryAddForm)
def field1_default_secondary(data):
    return u"Another dummy"

@form.widget_label(field=IDummySchema['field1'], context=IDummySchema)
def field1_label(data):
    return u"A label"

@form.button_label(button=EditForm.buttons['apply'])
def apply_button_label(data):
    return u"Computed label"
    
@form.button_label(button=DummySecondaryAddForm.buttons['add'], form=DummySecondaryAddForm)
def add_button_secondary(data):
    return u"Computed add button"

class TestValueDecorators(unittest.TestCase):

    def setUp(self):
        setupFormDefaults()
        
        grok('plone.directives.form.meta')
        grok('plone.directives.form.tests.test_value')
        
    def tearDown(self):
        zope.component.testing.tearDown()
        
    def test_default_value(self):
        
        add_form = DummyAddForm(Folder(), TestRequest())
        add_form.update()
        self.assertEquals(u"A dummy", add_form.widgets['field1'].value)
        
        edit_form = DummyEditForm(Dummy(), TestRequest())
        edit_form.update()
        self.assertEquals(u"Field 1 default", edit_form.widgets['field1'].value)
        
        secondary_add_form = DummySecondaryAddForm(Folder(), TestRequest())
        secondary_add_form.update()
        self.assertEquals(u"Another dummy", secondary_add_form.widgets['field1'].value)
    
    def test_widget_label(self):
        
        add_form = DummyAddForm(Folder(), TestRequest())
        add_form.update()
        self.assertEquals(u"Field one", add_form.widgets['field1'].label)
        self.assertEquals(u"Field two", add_form.widgets['field2'].label)
        
        edit_form = DummyEditForm(Dummy(), TestRequest())
        edit_form.update()
        self.assertEquals(u"A label", edit_form.widgets['field1'].label)
        self.assertEquals(u"Field two", edit_form.widgets['field2'].label)

    def test_button_label(self):
        
        add_form = DummyAddForm(Folder(), TestRequest())
        add_form.update()
        self.assertEquals(u"Add", add_form.actions['add'].title)
        
        secondary_add_form = DummySecondaryAddForm(Folder(), TestRequest())
        secondary_add_form.update()
        self.assertEquals(u"Computed add button", secondary_add_form.actions['add'].title)
        
        edit_form = DummyEditForm(Dummy(), TestRequest())
        edit_form.update()
        self.assertEquals(u"Computed label", edit_form.actions['apply'].title)
    
    def test_method_not_changed(self):
        self.assertEquals(u"Computed add button", add_button_secondary(None))
    
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestValueDecorators),
        ))