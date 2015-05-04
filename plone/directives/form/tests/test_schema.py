"""This module tests BBB for directives that were moved to plone.autoform."""

import unittest

from zope.interface import Interface

import zope.component.testing
from zope.testing import doctest

from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY
from plone.supermodel.model import Schema

from grokcore.component.testing import grok

from plone.directives import form

from plone.autoform.interfaces import OMITTED_KEY, WIDGETS_KEY, MODES_KEY, ORDER_KEY
from plone.autoform.interfaces import READ_PERMISSIONS_KEY, WRITE_PERMISSIONS_KEY

from plone.rfc822.interfaces import IPrimaryField


class DummyWidget(object):
    pass


class TestSchemaDirectives(unittest.TestCase):

    def setUp(self):
        configuration = """\
        <configure xmlns="http://namespaces.zope.org/zope">

            <include package="Products.Five" file="configure.zcml" />
            <include package="plone.directives.form" />

        </configure>
        """
        from StringIO import StringIO
        from zope.configuration import xmlconfig
        xmlconfig.xmlconfig(StringIO(configuration))

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

        self.assertEquals({'foo': 'plone.directives.form.tests.test_schema.DummyWidget'},
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
                           ('foo', 'before', 'body'), ],
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

        self.failUnless(IPrimaryField.providedBy(IDummy['foo']))
        self.failUnless(IPrimaryField.providedBy(IDummy['bar']))
        self.failUnless(IPrimaryField.providedBy(IDummy['baz']))
        self.failIf(IPrimaryField.providedBy(IDummy['qux']))

    def test_misspelled_field(self):

        try:
            class IFoo(form.Schema):
                form.primary('fou')
                foo = zope.schema.TextLine()
        except ValueError:
            pass
        else:
            self.fail('Did not raise ValueError')

        try:
            class IBar(form.Schema):
                form.order_before(ber='*')
                bar = zope.schema.TextLine()
        except ValueError:
            pass
        else:
            self.fail('Did not raise ValueError')

        try:
            class IBaz(form.Schema):
                form.omitted('buz')
                baz = zope.schema.TextLine()
        except ValueError:
            pass
        else:
            self.fail('Did not raise ValueError')

    def test_derived_class_fields(self):

        class IFoo(form.Schema):
            foo = zope.schema.TextLine()

        class IBar(IFoo):
            form.order_after(foo='bar')
            bar = zope.schema.TextLine()

        self.assertEquals(
            [('foo', 'after', 'bar'), ], IBar.queryTaggedValue(ORDER_KEY))

    def test_schema_without_model_not_grokked(self):

        class IFoo(Schema):
            pass

        self.assertEquals(None, IFoo.queryTaggedValue(FILENAME_KEY))
        self.assertEquals(None, IFoo.queryTaggedValue(SCHEMA_NAME_KEY))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSchemaDirectives),
        doctest.DocFileSuite('schema.txt',
                             setUp=zope.component.testing.setUp,
                             tearDown=zope.component.testing.tearDown),
    ))
