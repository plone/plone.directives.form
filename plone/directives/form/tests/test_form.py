import unittest
from plone.mocktestcase import MockTestCase

import zope.schema

from grokcore.component.testing import grok, grok_component

from plone.directives.form import schema, form

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY

class DummyWidget(object):
    pass

class TestSchemaDirectives(MockTestCase):

    def setUp(self):
        super(TestSchemaDirectives, self).setUp()
        grok('plone.directives.form.form')

    def test_schema_directives_store_tagged_values(self):
        
        class IDummy(schema.Schema):
            
            form.omitted('foo', 'bar')
            form.widget(foo='some.dummy.Widget', baz='other.Widget')
            form.mode(bar='hidden')
            form.order_before(baz='title')
            form.order_after(qux='title')
            
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
            
        self.replay()
        
        self.assertEquals(None, IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(ORDER_KEY))
        
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
        
    def test_widget_supports_instances_and_strings(self):
        
        class IDummy(schema.Schema):
            
            form.widget(foo=DummyWidget)
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        self.replay()
        
        self.assertEquals(None, IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(ORDER_KEY))
        
        grok_component('IDummy', IDummy)
        
        self.assertEquals({'foo': 'plone.directives.form.tests.test_form.DummyWidget'},
                  IDummy.queryTaggedValue(WIDGETS_KEY))
        
    def test_schema_directives_extend_existing_tagged_values(self):
        
        class IDummy(schema.Schema):
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
        
        class IDummy(schema.Schema):
            
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
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
            
        self.replay()
        
        self.assertEquals(None, IDummy.queryTaggedValue(WIDGETS_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(OMITTED_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(MODES_KEY))
        self.assertEquals(None, IDummy.queryTaggedValue(ORDER_KEY))
        
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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSchemaDirectives))
    return suite
