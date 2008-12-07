import unittest
import zope.app.testing.placelesssetup

from zope.interface import Interface

import zope.component.testing
from zope.testing import doctest

from plone.supermodel.interfaces import FILENAME_KEY, SCHEMA_NAME_KEY

from plone.directives.form.schema import Schema, model

from grokcore.component.testing import grok, grok_component

class TestDirectives(unittest.TestCase):
    
    def setUp(self):
        grok('plone.directives.form.schema')
        
    def teatDown(self):
        zope.component.testing.tearDown(self)
    
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
        unittest.makeSuite(TestDirectives),
        doctest.DocFileSuite('schema.txt',
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown),
        ))