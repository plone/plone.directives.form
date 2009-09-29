import unittest
import zope.app.testing.placelesssetup

from plone.mocktestcase import MockTestCase

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

class DummyWidget(object):
    pass

class TestSchemaDirectives(MockTestCase):

    def setUp(self):
        super(TestSchemaDirectives, self).setUp()
        grok('plone.directives.form.meta')

    def test_schema_directives_store_tagged_values(self):
        
        class IDummy(form.Schema):
            
            form.omitted('foo', 'bar')
            form.widget(foo='some.dummy.Widget', baz='other.Widget')
            form.mode(bar='hidden')
            form.order_before(baz='title')
            form.order_after(qux='title')
            form.read_permission(foo='zope2.View')
            form.write_permission(foo='cmf.ModifyPortalContent')
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
            
        self.replay()
        
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
        self.assertEquals({'foo': 'true',
                           'bar': 'true'},
                          IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals({'bar': 'hidden'},
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
            
        self.replay()
        
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
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        IDummy.setTaggedValue(WIDGETS_KEY, {'alpha': 'some.Widget'})
            
        self.replay()
        
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
            
        self.replay()
        
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
        self.assertEquals({'foo': 'true',
                           'bar': 'true'},
                          IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals({'bar': 'hidden', 'foo': 'display'},
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
            
        self.replay()
        
        self.failIf(IPrimaryField.providedBy(IDummy['foo']))
        self.failIf(IPrimaryField.providedBy(IDummy['bar']))
        self.failIf(IPrimaryField.providedBy(IDummy['baz']))
        self.failIf(IPrimaryField.providedBy(IDummy['qux']))
        
        grok_component('IDummy', IDummy)
        
        self.failUnless(IPrimaryField.providedBy(IDummy['foo']))
        self.failUnless(IPrimaryField.providedBy(IDummy['bar']))
        self.failUnless(IPrimaryField.providedBy(IDummy['baz']))
        self.failIf(IPrimaryField.providedBy(IDummy['qux']))
    
    def test_schema_without_model_not_grokked(self):
        
        class IFoo(Schema):
            pass
            
        self.assertEquals(True, grok_component('IFoo', IFoo))
        self.assertEquals(None, IFoo.queryTaggedValue(FILENAME_KEY))
        self.assertEquals(None, IFoo.queryTaggedValue(SCHEMA_NAME_KEY))

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