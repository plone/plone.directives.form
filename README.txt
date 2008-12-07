=====================
plone.directives.form
=====================

This package provides optional, Grok-like directives for configuring
forms using XML schemata as defined by plone.supermodel and/or using widget
form layout as defined by plone.autoform. It depends on five.grok, which in
turn depends on the various re-usable grokcore.* packages, but not Grok itself.

Schemata loaded from XML
------------------------

If you want to create a concrete interface, with a real module path, from
a plone.supermodel XML file, you can do::

    from plone.directives import form
    class IMySchema(form.Schema):
        form.model('myschema.xml')
        
The file will be loaded from the directory where the .py file for the
interface is located, unless an absolute path is given.

If the interface contains additional schema fields, they will add to and
override fields defined in the XML file.

See tests/schema.txt for more details.

Form widget hints
-----------------

The plone.autoform package provides the ability to generate a form from a
schema, using hints stored in tagged values on that schema to control form's
layout and field widgets. Those hints can be set using directives in this
package.

Below is an example that exercises the various directives::

    from plone.directives import form
    from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

    class IMySchema(form.Schema):
    
        # Add a new fieldset and put the 'footer' and 'dummy' fields in it.
        # If the same fieldset is defined multiple times, the definitions
        # will be merged, with the label from the first fieldset taking
        # precedence.
        
        form.fieldset('extra', 
                label=u"Extra info",
                fields=['footer', 'dummy']
            )

        title = schema.TextLine(
                title=u"Title"
            )
    
        summary = schema.Text(
                title=u"Summary",
                description=u"Summary of the body",
                readonly=True
            )
    
        body = schema.Text(
                title=u"Body text",
                required=False,
                default=u"Body text goes here"
            )
        form.widget(body='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
                       
        footer = schema.Text(
                title=u"Footer text",
                required=False
            )
        form.widget(footer=WysiwygFieldWidget)
    
        dummy = schema.Text(
                title=u"Dummy"
            )
        form.omitted('dummy')
    
        secret = schema.TextLine(
                title=u"Secret",
                default=u"Secret stuff"
            )
        form.mode(secret='hidden')
        
        not_last = schema.TextLine(
                title=u"Not last",
            )
        form.before(not_last='summary')

Here, we have placed the directives immediately after the fields they
affect, but they could be placed anywhere in the interface body. All the
directives can take multiple values, usually in the form fieldname='value'.
The 'omitted()' directive takes a list of omitted field names instead. The
'widget()' directive allows widgets to be set either as a dotted name, or
using an imported field widget factory. The 'before()' directive has a 
corresponding 'after' directive.