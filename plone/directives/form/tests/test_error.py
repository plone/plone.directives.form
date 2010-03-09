import unittest

import zope.component.testing

from zope.interface import implements, Interface
from zope import schema

from zope.schema.interfaces import TooSmall

from grokcore.component.testing import grok

from z3c.form.form import Form
from z3c.form.field import Fields

from z3c.form.testing import setupFormDefaults, TestRequest

from plone.directives import form

class IFolder(Interface):
    pass

class IFolder2(Interface):
    pass

class IDummySchema(Interface):
    
    field1 = schema.Int(title=u"Field one", min=10, required=True)
    field2 = schema.Int(title=u"Field two", min=10, required=False)

class Folder(object):
    implements(IFolder)

class Folder2(object):
    implements(IFolder2)

class DummyForm(Form):
    
    ignoreContext = True
    fields = Fields(IDummySchema)

class DummySecondaryForm(Form):
    
    ignoreContext = True
    fields = Fields(IDummySchema)

@form.error_message(error=TooSmall, field=IDummySchema['field1'], form=DummySecondaryForm)
def field1ErrorSecondForm(value):
    return u"Field 1 error second form"

@form.error_message(error=TooSmall, field=IDummySchema['field1'], content=IFolder2)
def field1ErrorContext(value):
    return u"Field 1 error context"

@form.error_message(error=TooSmall, field=IDummySchema['field1'])
def field1Error(value):
    return u"Field 1 error"


class TestErrorMessageDecorator(unittest.TestCase):

    def setUp(self):
        setupFormDefaults()
        
        grok('plone.directives.form.meta')
        grok('plone.directives.form.tests.test_error')
        
    def tearDown(self):
        zope.component.testing.tearDown()
        
    def test_error_message_no_error(self):
        
        form = DummyForm(Folder(), TestRequest(form={'form.widgets.field1': u"10"}))
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(0, len(errors))
    
    def test_error_message_field_only(self):
        
        form = DummyForm(Folder(), TestRequest(form={'form.widgets.field1': u"5"}))
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(1, len(errors))
        self.assertEquals(u"Field 1 error", errors[0].message)

    def test_error_message_field_view(self):
        
        form = DummySecondaryForm(Folder(), TestRequest(form={'form.widgets.field1': u"5"}))
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(1, len(errors))
        self.assertEquals(u"Field 1 error second form", errors[0].message)
    
    def test_error_message_field_context(self):
        
        form = DummyForm(Folder2(), TestRequest(form={'form.widgets.field1': u"5"}))
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(1, len(errors))
        self.assertEquals(u"Field 1 error context", errors[0].message)
    
    def test_method_not_changed(self):
        self.assertEquals(u"Field 1 error", field1Error(None))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
