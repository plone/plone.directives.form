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
        
        form.widget(body='plone.app.z3cform.wysiwyg.WysiwygFieldWidget')
        form.primary('body')
        body = schema.Text(
                title=u"Body text",
                required=False,
                default=u"Body text goes here"
            )
        
        
        form.widget(footer=WysiwygFieldWidget)
        footer = schema.Text(
                title=u"Footer text",
                required=False
            )
        
        form.omitted('dummy')
        dummy = schema.Text(
                title=u"Dummy"
            )
        
        form.mode(secret='hidden')
        secret = schema.TextLine(
                title=u"Secret",
                default=u"Secret stuff"
            )
        
        form.order_before(not_last='summary')
        not_last = schema.TextLine(
                title=u"Not last",
            )
        

Here, we have placed the directives immediately before the fields they
affect, but they could be placed anywhere in the interface body. All the
directives can take multiple values, usually in the form fieldname='value'.
The 'omitted()' and 'primary()' directives take a list of field names instead.
The 'widget()' directive allows widgets to be set either as a dotted name, or
using an imported field widget factory. The 'order_before()' directive has a 
corresponding 'order_after()' directive.

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

context
  The type of context (e.g. an interface)

request
  The type of request (e.g. a layer marker interface). You can
  use 'layer' as an alias for 'request', but note that the data passed
  to the function will have a 'request' attribute only.

view
    The type of form (e.g. a form instance or interface). You can
    use 'form' as an alias for 'view', but note that the data passed to
    the function will have 'view' attribute only.

field
    The field instance (or a field interface).

widget
    The widget type (e.g. an interface).
    
You must specify either 'field' or 'widget'. The object passed to the
decorated function has an attribute for each descriminator.

There are two more decorators:

widget_label
  Provide a dynamic label for a widget. Takes the same discriminators as the
  `default_value` decorator.
  
button_label -- Provide a dynamic label for a button. Takes parameters
  content (alias context), request (alias layer), form (alias view),
  manager and button.

Please note the rather unfortunate differences in naming between the button 
descriptors (content vs. context, form vs. view) and the widget ones. The
descriptor will accept the same names, but the data object passed to the
function will only contain the names as defined in z3c.form, so be careful.

Form base classes
-----------------

If you need to create your own forms, this package provides a number of
convenient base classes that will be grokked much like a grok.View or 
grok.CodeView. The grokkers take care of wrapping the form in a plone.z3cform
FormWrapper as well.

The base classes can all be imported from plone.directives.form, e.g::

    from plone.directives import form
    from z3c.form import field
    
    class MyForm(form.Form):
        fields = field.Fields(IMyFormSchema)
        ...
        
The various options are:

Form
    A simple page form, basically a grokked and automatically wrapped version
    of z3c.form.form.Form.

SchemaForm
    A page form that uses plone.autoform. You must set the 'schema' class
    variable (or implement it as a property) to a schema interface form which
    the form will be built. Form widget hints will be taken into account.

AddForm
    A simple add form with "Add" and "Cancel" buttons. You must implement
    the create() and add() methods. See the z3c.form documentation for more
    details.

SchemaAddForm
    An add form using plone.autoform. Again, you must set the 'schema' class
    variable.

EditForm
    A simple edit form with "Save" and "Cancel" buttons. See the z3c.form 
    documentation for more details.

SchemaEditForm
    An edit form using plone.autoform. Again, you must set the 'schema' class
    variable.

DisplayForm
    A view with an automatically associated template (like grok.View), that
    is initialised with display widgets. See plone.autoform's WidgetsView
    for more details.

