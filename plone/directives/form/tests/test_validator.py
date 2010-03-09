import unittest

import zope.component.testing

from zope.interface import implements, Interface
from zope import schema

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
    
    field1 = schema.TextLine(title=u"Field one", required=True)
    field2 = schema.TextLine(title=u"Field two", required=False)

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

@form.validator(field=IDummySchema['field1'])
def validate_field1(value):
    if value == 'fail':
        raise schema.ValidationError(u"Field 1, form 1")

@form.validator(field=IDummySchema['field1'], view=DummySecondaryForm)
def validate_field1_secondary(value):
    if value == 'fail':
        raise schema.ValidationError(u"Field 1, form 2")

@form.validator(field=IDummySchema['field1'], context=IFolder2)
def validate_field1_context(value):
    if value == 'fail':
        raise schema.ValidationError(u"Field 1, context")

class TestValidatorDecorator(unittest.TestCase):

    def setUp(self):
        setupFormDefaults()
        
        grok('plone.directives.form.meta')
        grok('plone.directives.form.tests.test_validator')
        
    def tearDown(self):
        zope.component.testing.tearDown()
        
    def test_validator_calls_default(self):
        
        form = DummyForm(Folder(), TestRequest())
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(1, len(errors))
        self.assertEquals(u"Required input is missing.", errors[0].error.doc())
    
    def test_validator_no_error(self):
        
        form = DummyForm(Folder(), TestRequest(form={'form.widgets.field1': u"Value"}))
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(0, len(errors))
    
    def test_validator_field_only(self):
        
        form = DummyForm(Folder(), TestRequest(form={'form.widgets.field1': u"fail"}))
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(1, len(errors))
        self.assertEquals(u"Field 1, form 1", errors[0].error.args[0])
    
    def test_validator_field_view(self):
        
        form = DummySecondaryForm(Folder(), TestRequest(form={'form.widgets.field1': u"fail"}))
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(1, len(errors))
        self.assertEquals(u"Field 1, form 2", errors[0].error.args[0])
    
    def test_validator_field_context(self):
        
        form = DummyForm(Folder2(), TestRequest(form={'form.widgets.field1': u"fail"}))
        form.update()
        
        data, errors = form.extractData()
        self.assertEquals(1, len(errors))
        self.assertEquals(u"Field 1, context", errors[0].error.args[0])
    
    def test_method_not_changed(self):
        self.assertEquals(None, validate_field1(None))
        self.assertRaises(schema.ValidationError, validate_field1, 'fail')

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
