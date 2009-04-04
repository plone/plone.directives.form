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

Value adapters
--------------

z3c.form has the concept of a 'value adapter', a component that can provide
a value for an attribute (usually of widgets and buttons) at runtime. This
package comes with some helpful decorators to register value adapters for
computed values. For example::

    from plone.directives import form
    from zope import schema
    
    class IMySchema(form.Schema):
    
        title = schema.TextLine(title=u"Title")

    @form.default_value(field=IMySchema['title'])
    def default_title(data):
        return data.context.suggested_title
        
The decorator takes one or more discriminators. The available descriminators
for `default_value` are:

    context -- The type of context (e.g. an interface)
    request -- The type of request (e.g. a layer marker interface). You can
        use 'layer' as an alias for 'request', but note that the data passed
        to the function will have a 'request' attribute only.
    view -- The type of form (e.g. a form instance or interface). You can
        use 'form' as an alias for 'view', but note that the data passed to
        the function will have 'view' attribute only.
    field -- The field instance (or a field interface).
    widget -- The widget type (e.g. an interface).
    
You must specify either 'field' or 'widget'. The object passed to the
decorated function has an attribute for each descriminator.

There are two more decorators:

    widget_label -- Provide a dynamic label for a widget. Takes the same
        discriminators as the `default_value` decorator.
    button_label -- Provide a dynamic label for a button. Takes parameters
        content (alias context), request (alias layer), form (alias view),
        manager and button.

Please note the rather unfortunate differences in naming between the button 
descriptors (content vs. context, form vs. view) and the widget ones. The
descriptor will accept the same names, but the data object passed to the
function will only contain the names as defined in z3c.form, so be careful.
