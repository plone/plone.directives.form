import unittest
from plone.mocktestcase import MockTestCase

from zope.interface import Interface, implements, alsoProvides
from zope.component import getMultiAdapter, provideUtility

from zope.publisher.browser import TestRequest

import grokcore.component.testing

from zope.security.permission import Permission

from plone.directives import form
from five import grok

class ILayer(Interface):
    pass

class IDummy(Interface):
    pass

class IDummy2(Interface):
    pass

class Dummy(object):
    implements(IDummy)
    
    def absolute_url(self):
        return "http://dummy"

class Request(TestRequest):
    
    # Zope 2 requests have this
    def __setitem__(self, name, value):
        self._environ[name] = value

class TestFormDirectives(MockTestCase):

    def setUp(self):
        super(TestFormDirectives, self).setUp()
        
        grokcore.component.testing.grok('plone.directives.form.meta')
        
        provideUtility(Permission('zope2.View'), name='zope2.View')
        provideUtility(Permission('cmf.ModifyPortalContent'), name='cmf.ModifyPortalContent')
        provideUtility(Permission('cmf.AddPortalContent'), name='cmf.AddPortalContent')

    def test_form_grokker_with_directives(self):
        
        class TestForm(form.Form):
            grok.context(IDummy)
            grok.name('my-test-form')
            grok.layer(ILayer)
            grok.require('zope2.View')
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        alsoProvides(request, ILayer)
        
        view = getMultiAdapter((context, request), name="my-test-form")
        
        self.assertEquals(TestForm, view.form)

    def test_grokker_with_defaults(self):
        
        class TestForm(form.Form):
            grok.context(IDummy)
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.assertEquals(TestForm, view.form)

    def test_schema_form(self):
        
        class TestForm(form.SchemaForm):
            grok.context(IDummy)
            schema = IDummy2
            
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.assertEquals(TestForm, view.form)
        self.assertEquals(IDummy2, view.form.schema)
    
    def test_schema_form_implicit_schema(self):
        
        class TestForm(form.SchemaForm):
            grok.context(IDummy)
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.assertEquals(TestForm, view.form)
        self.assertEquals(IDummy, view.form.schema)
        
    def test_add_form(self):
        
        class TestForm(form.AddForm):
            grok.context(IDummy)
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.assertEquals(TestForm, view.form)
        
        self.assertEquals("http://dummy", view.form_instance.nextURL())
        view.form_instance.immediate_view = "http://other_view"
        self.assertEquals("http://other_view", view.form_instance.nextURL())

    def test_schema_add_form(self):
        
        class TestForm(form.SchemaAddForm):
            grok.context(IDummy)
            schema = IDummy2
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.assertEquals(TestForm, view.form)
        self.assertEquals(IDummy2, view.form.schema)
    
    # Note: No implicit schema-from-context here, since context of add form
    #  is container.
    
    def test_edit_form(self):
        
        class TestForm(form.EditForm):
            grok.context(IDummy)
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.assertEquals(TestForm, view.form)

    def test_schema_edit_form(self):
        
        class TestForm(form.SchemaEditForm):
            grok.context(IDummy)
            schema = IDummy2
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.assertEquals(TestForm, view.form)
        self.assertEquals(IDummy2, view.form.schema)
        
    def test_schema_edit_form_implicit_schema(self):
        
        class TestForm(form.SchemaEditForm):
            grok.context(IDummy)
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.assertEquals(TestForm, view.form)
        self.assertEquals(IDummy, view.form.schema)

    def test_display_form_with_schema(self):
        
        # Note: We're not testing view registration, since that is done
        # by the standard five.grok View grokker
        
        class TestForm(form.DisplayForm):
            grok.context(IDummy)
            schema = IDummy2
            
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        self.assertEquals(IDummy2, TestForm.schema)
    
    def test_display_form_implicit_schema(self):

        # Note: We're not testing view registration, since that is done
        # by the standard five.grok View grokker
        
        class TestForm(form.DisplayForm):
            grok.context(IDummy)
        
        self.replay()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        self.assertEquals(IDummy, TestForm.schema)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFormDirectives))
    return suite
