import warnings
import unittest
import zope.component.testing

from zope.interface import Interface, implements, alsoProvides
from zope.component import getMultiAdapter, provideUtility
from zope.configuration.config import ConfigurationExecutionError

from zope.publisher.browser import TestRequest

import grokcore.component.testing
import grokcore.view.interfaces

from zope.security.permission import Permission

from plone.z3cform.layout import FormWrapper

from plone.directives import form
from five import grok

import plone.directives.form.meta

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

# ignore warnings about unassociated templates, since the way we do the tests
# mean the association happens after the module is grokked
warnings.filterwarnings("ignore", ".*unassociated template.*testformwithtemplate.*")

class TestFormDirectives(unittest.TestCase):

    def setUp(self):
        
        # On Zope 2.10, the default is True, on 2.12 it's False
        self.defaultWrap = plone.directives.form.meta.DEFAULT_WRAP
        plone.directives.form.meta.DEFAULT_WRAP = False
        
        grokcore.component.testing.grok('grokcore.component.meta')
        grokcore.component.testing.grok('grokcore.security.meta')
        grokcore.component.testing.grok('grokcore.view.meta.templates')
        grokcore.component.testing.grok('grokcore.view.meta.views')
        grokcore.component.testing.grok('grokcore.view.meta.skin')
        grokcore.component.testing.grok('five.grok.meta')
        grokcore.component.testing.grok('plone.directives.form.meta')
        
        grokcore.component.testing.grok('grokcore.view.templatereg')
        
        provideUtility(Permission('zope2.View'), name='zope2.View')
        provideUtility(Permission('cmf.ModifyPortalContent'), name='cmf.ModifyPortalContent')
        provideUtility(Permission('cmf.AddPortalContent'), name='cmf.AddPortalContent')
    
    def tearDown(self):
        zope.component.testing.tearDown()
        plone.directives.form.meta.DEFAULT_WRAP = self.defaultWrap
    
    def test_form_grokker_with_directives(self):
        
        class TestForm(form.Form):
            grok.context(IDummy)
            grok.name('my-test-form')
            grok.layer(ILayer)
            grok.require('zope2.View')
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        alsoProvides(request, ILayer)
        
        view = getMultiAdapter((context, request), name="my-test-form")
        
        self.failUnless(issubclass(view.form, TestForm))

    def test_grokker_with_defaults(self):
        
        class TestForm(form.Form):
            grok.context(IDummy)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))

    def test_schema_form(self):
        
        class TestForm(form.SchemaForm):
            grok.context(IDummy)
            schema = IDummy2
            
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.assertEquals(IDummy2, view.form.schema)
    
    def test_schema_form_implicit_schema(self):
        
        class TestForm(form.SchemaForm):
            grok.context(IDummy)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.assertEquals(IDummy, view.form.schema)
        
    def test_add_form(self):
        
        class TestForm(form.AddForm):
            grok.context(IDummy)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        
        self.assertEquals("http://dummy", view.form_instance    .nextURL())
        view.form_instance.immediate_view = "http://other_view"
        self.assertEquals("http://other_view", view.form_instance.nextURL())

    def test_schema_add_form(self):
        
        class TestForm(form.SchemaAddForm):
            grok.context(IDummy)
            schema = IDummy2
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.assertEquals(IDummy2, view.form.schema)
    
    # Note: No implicit schema-from-context here, since context of add form
    #  is container.
    
    def test_edit_form(self):
        
        class TestForm(form.EditForm):
            grok.context(IDummy)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))

    def test_schema_edit_form(self):
        
        class TestForm(form.SchemaEditForm):
            grok.context(IDummy)
            schema = IDummy2
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.assertEquals(IDummy2, view.form.schema)
        
    def test_schema_edit_form_implicit_schema(self):
        
        class TestForm(form.SchemaEditForm):
            grok.context(IDummy)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
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
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        self.assertEquals(IDummy, TestForm.schema)
    
    def test_wrap(self):
        
        class TestForm(form.Form):
            grok.context(IDummy)
            form.wrap()
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.failUnless(isinstance(view, FormWrapper))
    
    def test_wrap_false(self):
        
        class TestForm(form.Form):
            grok.context(IDummy)
            form.wrap(False)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.failUnless(isinstance(view, TestForm))
    
    def test_nowrap(self):
        
        class TestForm(form.Form):
            grok.context(IDummy)
            form.wrap(False)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.failUnless(isinstance(view, TestForm))
    
    def test_wrap_default(self):
        
        # Simulate Zope 2.10 default
        plone.directives.form.meta.DEFAULT_WRAP = True
        
        class TestForm(form.Form):
            grok.context(IDummy)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.failUnless(isinstance(view, FormWrapper))
    
    def test_wrap_default_wrap_false(self):
        # Simulate Zope 2.10 default
        plone.directives.form.meta.DEFAULT_WRAP = True
        
        class TestForm(form.Form):
            grok.context(IDummy)
            form.wrap(False)
        
        grokcore.component.testing.grok_component('TestForm', TestForm)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testform")
        
        self.failUnless(issubclass(view.form, TestForm))
        self.failUnless(isinstance(view, TestForm))
    
    def test_template(self):
        
        class TestFormWithTemplate(form.Form):
            grok.context(IDummy)
        
        grokcore.component.testing.grok(__name__)
        
        grokcore.component.testing.grok_component('TestFormWithTemplate', TestFormWithTemplate)
        
        context = Dummy()
        request = Request()
        
        view = getMultiAdapter((context, request), name="testformwithtemplate")
        
        self.failUnless(issubclass(view.form, TestFormWithTemplate))
        self.failUnless(grokcore.view.interfaces.ITemplate.providedBy(view.template))
    
    def test_template_and_render(self):
        
        class TestFormWithTemplate(form.Form):
            grok.context(IDummy)
            
            def render(self):
                return u"My custom renderer"
        
        grokcore.component.testing.grok(__name__)
        
        self.assertRaises(ConfigurationExecutionError,
            grokcore.component.testing.grok_component,
            'TestFormWithTemplate', TestFormWithTemplate)
    
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
