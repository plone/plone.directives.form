import unittest
import zope.app.testing.placelesssetup

from zope.interface import Interface

import zope.component.testing
from zope.testing import doctest

from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY

from plone.directives.form.schema import Schema, model

from grokcore.component.testing import grok, grok_component

from plone.directives import form

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

from plone.rfc822.interfaces import IPrimaryField

from martian.error import GrokImportError

class DummyWidget(object):
    pass

class TestSchemaDirectives(unittest.TestCase):

    def setUp(self):
        grok('plone.directives.form.meta')

    def tearDown(self):
        zope.component.testing.tearDown()
    
    def test_schema_directives_store_tagged_values(self):
        
        class IDummy(form.Schema):
            
            form.omitted('foo', 'bar')
            form.omitted(form.Schema, 'qux')
            form.no_omit(form.Schema, 'bar')
            form.widget(foo='some.dummy.Widget', baz='other.Widget')
            form.mode(bar='hidden')
            form.mode(form.Schema, bar='input')
            form.order_before(baz='title')
            form.order_after(qux='title')
            form.read_permission(foo='zope2.View')
            form.write_permission(foo='cmf.ModifyPortalContent')
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
            
        self.assertEquals(None, IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(ORDER_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(READ_PERMISSIONS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(WRITE_PERMISSIONS_KEY))
        
        grok_component('IDummy', IDummy)
        
        self.assertEquals({'foo': 'some.dummy.Widget',
                           'baz': 'other.Widget'},
                          IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals([(Interface, 'foo', 'true'),
                           (Interface, 'bar', 'true'),
                           (form.Schema, 'qux', 'true'),
                           (form.Schema, 'bar', 'false')],
                          IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals([(Interface, 'bar', 'hidden'),
                           (form.Schema, 'bar', 'input')],
                          IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals([('baz', 'before', 'title',),
                           ('qux', 'after', 'title')],
                          IDummy.queryTaggedValue(ORDER_KEY))
        self.assertEquals({'foo': 'zope2.View'},
                          IDummy.queryTaggedValue(READ_PERMISSIONS_KEY))
        self.assertEquals({'foo': 'cmf.ModifyPortalContent'},
                          IDummy.queryTaggedValue(WRITE_PERMISSIONS_KEY))
                                  
    def test_widget_supports_instances_and_strings(self):
        
        class IDummy(form.Schema):
            
            form.widget(foo=DummyWidget)
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        self.assertEquals(None, IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(ORDER_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(READ_PERMISSIONS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(WRITE_PERMISSIONS_KEY))
        
        grok_component('IDummy', IDummy)
        
        self.assertEquals({'foo': 'plone.directives.form.tests.test_schema.DummyWidget'},
                  IDummy.queryTaggedValue(WIDGETS_KEY))
        
    def test_schema_directives_extend_existing_tagged_values(self):
        
        class IDummy(form.Schema):
            form.widget(foo='some.dummy.Widget')
            
            alpha = zope.schema.TextLine(title=u"Alpha")
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        IDummy.setTaggedValue(WIDGETS_KEY, {'alpha': 'some.Widget'})
            
        self.assertEquals({'alpha': 'some.Widget'}, IDummy.queryTaggedValue(WIDGETS_KEY))
        
        grok_component('IDummy', IDummy)
        
        self.assertEquals({'alpha': 'some.Widget', 'foo': 'some.dummy.Widget'},
                          IDummy.queryTaggedValue(WIDGETS_KEY))
        
    def test_multiple_invocations(self):
        
        class IDummy(form.Schema):
            
            form.omitted('foo')
            form.omitted('bar')
            form.widget(foo='some.dummy.Widget')
            form.widget(baz='other.Widget')
            form.mode(bar='hidden')
            form.mode(foo='display')
            form.order_before(baz='title')
            form.order_after(baz='qux')
            form.order_after(qux='bar')
            form.order_before(foo='body')
            form.read_permission(foo='zope2.View', bar='zope2.View')
            form.read_permission(baz='random.Permission')
            form.write_permission(foo='cmf.ModifyPortalContent')
            form.write_permission(baz='another.Permission')
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
            
        self.assertEquals(None, IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(ORDER_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(READ_PERMISSIONS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(WRITE_PERMISSIONS_KEY))
        
        grok_component('IDummy', IDummy)
        
        self.assertEquals({'foo': 'some.dummy.Widget',
                           'baz': 'other.Widget'},
                          IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals([(Interface, 'foo', 'true'),
                           (Interface, 'bar', 'true')],
                          IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals([(Interface, 'bar', 'hidden'),
                           (Interface, 'foo', 'display')],
                          IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals([('baz', 'before', 'title'),
                           ('baz', 'after', 'qux'),
                           ('qux', 'after', 'bar'),
                           ('foo', 'before', 'body'),],
                          IDummy.queryTaggedValue(ORDER_KEY))
        self.assertEquals({'foo': 'zope2.View', 'bar': 'zope2.View', 'baz': 'random.Permission'},
                          IDummy.queryTaggedValue(READ_PERMISSIONS_KEY))
        self.assertEquals({'foo': 'cmf.ModifyPortalContent', 'baz': 'another.Permission'},
                          IDummy.queryTaggedValue(WRITE_PERMISSIONS_KEY))
    
    def test_primary_field(self):
        
        class IDummy(form.Schema):
            
            form.primary('foo')
            form.primary('bar', 'baz')
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
            
        self.failIf(IPrimaryField.providedBy(IDummy['foo']))
        self.failIf(IPrimaryField.providedBy(IDummy['bar']))
        self.failIf(IPrimaryField.providedBy(IDummy['baz']))
        self.failIf(IPrimaryField.providedBy(IDummy['qux']))
        
        grok_component('IDummy', IDummy)
        
        self.failUnless(IPrimaryField.providedBy(IDummy['foo']))
        self.failUnless(IPrimaryField.providedBy(IDummy['bar']))
        self.failUnless(IPrimaryField.providedBy(IDummy['baz']))
        self.failIf(IPrimaryField.providedBy(IDummy['qux']))
    
    def test_misspelled_field(self):
        
        class IFoo(form.Schema):
            form.primary('fou')
            foo = zope.schema.TextLine()
        
        class IBar(form.Schema):
            form.order_before(ber='*')
            bar = zope.schema.TextLine()
        
        class IBaz(form.Schema):
            form.omitted('buz')
            baz = zope.schema.TextLine()
            
        self.assertRaises(GrokImportError, grok_component, 'IFoo', IFoo)
        self.assertRaises(GrokImportError, grok_component, 'IBar', IBar)
        self.assertRaises(GrokImportError, grok_component, 'IBaz', IBaz)

    def test_derived_class_fields(self):
        
        class IFoo(form.Schema):
            foo = zope.schema.TextLine()
        
        class IBar(IFoo):
            form.order_after(foo='bar')
            bar = zope.schema.TextLine()
        
        grok_component('IBar', IBar)
        
        self.assertEquals([('foo', 'after', 'bar'),], IBar.queryTaggedValue(ORDER_KEY))
    
    def test_schema_without_model_not_grokked(self):
        
        class IFoo(Schema):
            pass
            
        self.assertEquals(True, grok_component('IFoo', IFoo))
        self.assertEquals(None, IFoo.queryTaggedValue(FILENAME_KEY))
        self.assertEquals(None, IFoo.queryTaggedValue(SCHEMA_NAME_KEY))
    
    def test_non_schema_with_directives_raises_error(self):
        
        class IFoo(Interface):
            form.order_before(foo='*')
            foo = zope.schema.TextLine()
        
        class IBar(Interface):
            form.primary('bar')
            bar = zope.schema.TextLine()
        
        self.assertRaises(GrokImportError, grok_component, 'IFoo', IFoo)
        self.assertRaises(GrokImportError, grok_component, 'IBar', IBar)
        
    def test_non_schema_not_grokked(self):
        
        class IFoo(Interface):
            model('dummy.xml')
            
        self.assertEquals(False, grok_component('IFoo', IFoo))
        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSchemaDirectives),
        doctest.DocFileSuite('schema.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown),
        ))
