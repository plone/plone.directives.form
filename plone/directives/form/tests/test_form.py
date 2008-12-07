import unittest
import mocker
from plone.mocktestcase import MockTestCase

from zope.interface import Interface
import zope.schema

from grokcore.component.testing import grok, grok_component
import five.grok

from plone.directives.form import schema, form

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.CMFCore.interfaces import IFolderish

from plone.autoform.interfaces import FORMDATA_KEY

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
        
        self.assertEquals(None, IDummy.queryTaggedValue(FORMDATA_KEY))
        grok_component('IDummy', IDummy)
        self.assertEquals({u'widgets': [('foo', 'some.dummy.Widget'), ('baz', 'other.Widget')],
                           u'omitted': [('foo', 'true'), ('bar', 'true')],
                           u'before': [('baz', 'title')],
                           u'after': [('qux', 'title')],
                           u'modes': [('bar', 'hidden')]},
                            IDummy.queryTaggedValue(FORMDATA_KEY))
        
    def test_widget_supports_instances_and_strings(self):
        
        class IDummy(schema.Schema):
            
            form.widget(foo=DummyWidget)
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        self.replay()
        
        self.assertEquals(None, IDummy.queryTaggedValue(FORMDATA_KEY))
        grok_component('IDummy', IDummy)
        self.assertEquals({u'widgets': [('foo', 'plone.directives.form.tests.test_form.DummyWidget')]}, 
                            IDummy.queryTaggedValue(FORMDATA_KEY))
        
    def test_schema_directives_extend_existing_tagged_values(self):
        
        class IDummy(schema.Schema):
            form.widget(foo='some.dummy.Widget')
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            
        IDummy.setTaggedValue(FORMDATA_KEY, {u'widgets': [('alpha', 'some.Widget')]})
            
        self.replay()
        
        self.assertEquals({u'widgets': [('alpha', 'some.Widget')]}, 
                            IDummy.queryTaggedValue(FORMDATA_KEY))
        grok_component('IDummy', IDummy)
        self.assertEquals({u'widgets': [('alpha', 'some.Widget'), ('foo', 'some.dummy.Widget')]}, 
                            IDummy.queryTaggedValue(FORMDATA_KEY))
        
    def test_multiple_invocations(self):
        
        class IDummy(schema.Schema):
            
            form.omitted('foo')
            form.omitted('bar')
            form.widget(foo='some.dummy.Widget')
            form.widget(baz='other.Widget')
            form.mode(bar='hidden')
            form.mode(foo='display')
            form.order_before(baz='title')
            form.order_before(foo='body')
            form.order_after(baz='qux')
            form.order_after(qux='bar')
            
            
            foo = zope.schema.TextLine(title=u"Foo")
            bar = zope.schema.TextLine(title=u"Bar")
            baz = zope.schema.TextLine(title=u"Baz")
            qux = zope.schema.TextLine(title=u"Qux")
            
        self.replay()
        
        self.assertEquals(None, IDummy.queryTaggedValue(FORMDATA_KEY))
        grok_component('IDummy', IDummy)
        self.assertEquals({u'widgets': [('foo', 'some.dummy.Widget'), ('baz', 'other.Widget')],
                           u'omitted': [('foo', 'true'), ('bar', 'true')],
                           u'before': [('baz', 'title'), ('foo', 'body')],
                           u'after': [('baz', 'qux'), ('qux', 'bar')],
                           u'modes': [('bar', 'hidden'), ('foo', 'display')]}, 
                            IDummy.queryTaggedValue(FORMDATA_KEY))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSchemaDirectives))
    return suite
