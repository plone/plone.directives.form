=====================
plone.directives.form
=====================

This package provides optional, Grok-like directives for configuring
forms, as defined by the `z3c.form`_ library, using XML schemata as defined by
`plone.supermodel`_ and/or using widget form layout as defined by
`plone.autoform`_. It depends on `five.grok`_, which in turn depends on the
various re-usable grokcore.* packages, but not Grok itself.

.. contents:: Contents

Installation
------------

To use this package you must first install it, either by depending on it
in your own ``setup.py`` (under the ``install_requires`` list), or by adding
it directly to your buildout.

This will pull in a number of dependencies. You probably want to pin those
down to known-good versions by using a known-good version set. See the
installation instructions of `five.grok`_ for a starting point.

You must also load the relevant configuration from ``meta.zcml`` and
``configure.zcml``. For example, you could use statements like the following
in your ``configure.zcml``::

    <include package="plone.directives.form" file="meta.zcml" />
    <include package="plone.directives.form" />
    
or if you declare dependencies in setup.py using install_requires::

    <includeDependencies package="." />
        
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

The `plone.autoform`_ package provides the ability to generate a form from a
schema, using hints stored in tagged values on that schema to control form's
layout and field widgets. Those hints can be set using directives in this
package.

Below is an example that exercises the various directives::

    from z3c.form.interfaces import IEditForm
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
        
        form.omitted('edit_only')
        form.no_omit(IEditForm, 'edit_only')
        edit_only = schema.TextLine(
                title = u'Only included on edit forms',
            )
        
        form.mode(secret='hidden')
        form.mode(IEditForm, secret='input')
        secret = schema.TextLine(
                title=u"Secret",
                default=u"Secret stuff (except on edit forms)"
            )
        
        form.order_before(not_last='summary')
        not_last = schema.TextLine(
                title=u"Not last",
            )
        

Here, we have placed the directives immediately before the fields they
affect, but they could be placed anywhere in the interface body. All the
directives can take multiple values, usually in the form
``fieldname='value'``.

The ``omitted()``, ``no_omit``, and ``primary()`` directives take a list of
field names instead. The ``widget()`` directive allows widgets to be set either
as a dotted name, or using an imported field widget factory. The
``order_before()`` directive has a  corresponding ``order_after()`` directive.

Value adapters
--------------

z3c.form has the concept of a "value adapter", a component that can provide
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
        
The decorator takes one or more discriminators. The available discriminators
for ``default_value`` are:

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
    
You must specify either ``field`` or ``widget``. The object passed to the
decorated function has an attribute for each discriminator.

There are two more decorators:

widget_label
  Provide a dynamic label for a widget. Takes the same discriminators as the
  ``default_value`` decorator.
  
button_label -- Provide a dynamic label for a button. Takes parameters
  content (alias context), request (alias layer), form (alias view),
  manager and button.

Please note the rather unfortunate differences in naming between the button 
descriptors (content vs. context, form vs. view) and the widget ones. The
descriptor will accept the same names, but the data object passed to the
function will only contain the names as defined in z3c.form, so be careful.

Validators
----------

By default, z3c.form uses fields' native validation, as implemented by the
``IField.validate()`` method, as well as field constraints (functions passed
as the ``constraint`` parameter to fields) and schema invariants (using the
``@zope.interface.invariant`` decorator in a schema interface). In addition,
you can define your own widget validators (for an individual field of the
form) and widget manager validators (which cover the entire form). This is
useful if you do not want to define a validator on the schema, e.g. because
the schema is also used elsewhere, or if you want to create a more generic
validator that is applied to any fields that match its discriminators.

This package provides a grokked decorator which you can use to define a simple
widget validator, called ``@form.validator()``::

    from plone.directives import form
    from zope import schema
    
    class IMySchema(form.Schema):
    
        title = schema.TextLine(title=u"Title")
    
    @form.validator(field=IMySchema['title'])
    def validateTitle(value):
        if value == value.upper():
            raise schema.ValidationError(u"Please don't shout")

The validator should return nothing if the field is valid, or raise an
``zope.schema.ValidationError`` exception with an error message.

The ``@form.validator()`` decorator can take various keyword arguments that
determine when the validator is invoked. These are:

context
  The type of context (e.g. an interface)

request
  The type of request (e.g. a layer marker interface).

view
    The type of form (e.g. a form instance or interface).

field
    The field instance (or a field interface).

widget
    The widget type (e.g. an interface).

Note that this validator function does not give access to the full context
of the standard validator, such as the field, widget, context or request.
If you need that, you can create a standard validator adapter, e.g. using
``grok.Adapter``. See the `z3c.form`_ documentation for details.

Also note that the standard field validator will be called before the custom
validator is invoked. If you need to override the validator wholesale, you
can again do so with a custom adapter.

Error messages
--------------

When using custom validators, it is easy to supply a tailored error message.
However, the error messages that arise from the default field validation
mechanism (e.g. when a required field is omitted) are by necessity more
generic. Sometimes, it may be necessary to override these messages to make
them more user friendly.

To customise an error message, you can use the ``@form.error_message`` grokked
decorator. For example::

    from plone.directives import form
    from zope import schema
    
    from zope.schema.interfaces import TooShort
    
    class IMySchema(form.Schema):
    
        title = schema.TextLine(title=u"Title", min_length=2)
    
    @form.error_message(error=TooShort, field=IMySchema['title'])
    def titleTooShort(value):
        return u"The title '%s' is too short" % value

The decorated function will be called when constructing an error message for
the given field. It should return a unicode string or translatable message.
The value passed is the value that failed validation.

The ``@form.error_message`` validator takes keyword arguments that determine
when the message is used. It is possible to register a generic error message
for a given type of error that applies to all fields, or, as shown above,
a message specific to an individual field and error. The latter is more
common. In general, you should be careful if you omit either or both of the
``error`` and ``field`` discriminators.

error
    An exception class that represents the error. All errors inherit from
    ``zope.interface.Invalid``, and most error also inherit from
    ``zope.schema.interfaces.ValidationError``. See below for a list of
    common exception types.
request
    The current request. Use this to tie the error to a specific browser
    layer interface.
widget
    The widget that was used. May be either a widget interface or a specific
    widget class.
field
    The field that was used, normally given as a field instance obtained from
    an interface, as illustrated above.
form
    The current form, either as a class or an interface. This is useful if
    the same interface is used in more than one form, but you only want the
    error to be shown in one form.
content
    The content item that is acting as the context for the form. May be given
    as either an interface or a class.

None of these parameters is required, but you would normally supply at least
``error``. In most cases, you should also supply the ``field``, as shown
above.

The most common validation error exception types are defined in
``zope.schema``, and can be imported from ``zope.schema.interfaces``:

* ``RequiredMissing``, used when a required field is submitted without a value
* ``WrongType``, used when a field is passed a value of an invalid type
* ``TooBig`` and ``TooSmall``, used when a value is outside the ``min`` and/or
  ``max`` range specified for ordered fields (e.g. numeric or date fields)
* ``TooLong`` and ``TooShort``, used when a value is outside the
  ``min_length`` and/or ``max_length`` range specified for length-aware fields
  (e.g. text or sequence fields)
* ``InvalidValue``, used when a value is invalid, e.g. a non-ASCII character
  passed to an ASCII field
* ``ConstraintNotSatisfied``, used when a ``constraint`` method returns
  ``False``
* ``WrongContainedType``, used if an object of an invalid type is added
  to a sequence (i.e. the type does not conform to the field's
  ``value_type``)
* ``NotUnique``, used if a uniqueness constraint is violated
* ``InvalidURI``, used for ``URI`` fields if the value is not a valid URI
* ``InvalidId``, used for ``Id`` fields if the value is not a valid id
* ``InvalidDottedName``, used for ``DottedName`` fields if the value is not
  a valid dotted name

Form base classes
-----------------

If you need to create your own forms, this package provides a number of
convenient base classes that will be grokked much like a ``grok.View``.

In Zope 2.10, the grokkers take care of wrapping the form in a
`plone.z3cform`_ FormWrapper as well. In Zope 2.12 and later, there is no
wrapper by default. If you want one (e.g. if you are using a custom template
and you need it to work in both Zope 2.10 and 2.12), you can use the
``form.wrapped()`` directive in the form class.

The base classes can all be imported from ``plone.directives.form``, e.g::

    from five import grok
    from plone.directives import form, button
    from z3c.form import field
    
    class MyForm(form.Form):
        grok.context(ISomeContext)
        grok.require('zope2.View')
        
        fields = field.Fields(IMyFormSchema)
        
        @button.buttonAndHandler(u'Submit')
        def handleApply(self, action):
            data, errors = self.extractData()
            ...

The allowed directives are:

* ``grok.context()``, to specify the context of form view. If not given, the
  grokker will look for a module-level context, much like the standard
  ``grok.View``.
* ``grok.require()``, to specify a permission. The default is ``zope2.View``
  for standard forms, ``cmf.ModifyPortalContent`` for edit forms, and
  ``cmf.AddPortalContent`` for add forms.
* ``grok.layer()`` to specify a browser layer
* ``grok.name()`` to set a different name. By default your form will be 
  available as view @@yourformclassnamelowercase, but you can use 
  ``grok.name()`` to set name explicitly.
* ``form.wrapped()`` to wrap the form in a layout wrapper view. You can pass
  an argument of ``True`` or ``False`` to enable or disable wrapping. If no
  argument is given, it defaults to ``True``. If omitted, the global default
  is used, which is to wrap in Zope 2.11 or earlier, and to not wrap in Zope
  2.12 or later
  
More complex example how to use Grok directives with a form::

        from plone.directives import form
        from Products.CMFCore.interfaces import ISiteRoot
  
        class CompanyCreationForm(form.SchemaForm):
            """ A sample form how to "create companies". 
            
            """
                      
            # Which plone.directives.form.Schema subclass is used to define 
            # fields for this form (not shown on this example)
            schema = ICompanyCreationFormSchema
            
            # Permission required to view/submit the form
            grok.require("cmf.ManagePortal")
            
            # The form does not care about the context object
            # and  should not try to extract field value
            # defaults out of it
            ignoreContext = True
            
            # This form is available at the site root only
            grok.context(ISiteRoot)
        
            # The form will be available in Plone site root only
            # Use http://yourhost/@@create_company URL to access this form
            grok.name("create_company")
    
    


Each of the form base classes has a "schema" equivalent, which can be
initialised with a ``schema`` attribute instead of the ``fields`` attribute.
These forms use `plone.autoform`_'s ``AutoExtensibleForm`` as a base class,
allowing schema hints as shown above to be processed::
    
    from plone.directives import form
    from z3c.form import field
    
    class MyForm(form.SchemaForm):
        grok.context(ISomeContext)
        grok.require('zope2.View')
        
        schema = IMySchema
        
        @button.buttonAndHandler(u'Submit')
        def handleApply(self, action):
            data, errors = self.extractData()
            ...

Note that the ``schema`` can be omitted if you are using ``SchemaForm`` or
``SchemaEditForm`` and you have given an interface as the argument to
``grok.context()``. In this case, the context interface will be used as the
default schema.

The available form base classes are:

Form
    A simple page form, basically a grokked version of ``z3c.form.form.Form``.

SchemaForm
    A page form that uses `plone.autoform`_. You must set the ``schema`` class
    variable (or implement it as a property) to a schema interface form which
    the form will be built. Form widget hints will be taken into account.

AddForm
    A simple add form with "Add" and "Cancel" buttons. You must implement
    the ``create()`` and ``add()`` methods. See the `z3c.form`_ documentation
    for more details.

SchemaAddForm
    An add form using `plone.autoform`_. Again, you must set the ``schema``
    class variable.

EditForm
    A simple edit form with "Save" and "Cancel" buttons. See the `z3c.form`_
    documentation for more details.

SchemaEditForm
    An edit form using `plone.autoform`_. Again, you must set the ``schema``
    class variable.

DisplayForm
    A view with an automatically associated template (like ``grok.View``),
    that is initialised with display widgets. See `plone.autoform`_'s
    ``WidgetsView`` for more details.

All of the grokked form base classes above support associating a custom 
template with the form. This uses the same semantics as ``grok.View``. See
`grokcore.view`_ for details, but briefly:

* If you want to completely customise rendering, you can override the 
  ``render()`` method.
* If you want to use a page template to render a form called ``MyForm`` in
  the module ``my.package.forms``, create a directory inside ``my.package``
  called ``forms_templates`` (the prefix should match the module name),
  and place a file there called ``myform.pt``.
* If you do neither, the default form template will be used, as is the 
  standard behaviour in z3c.form.

Note that the automatically associated form template can use ``grok.View``
methods, such as ``view.url()`` and ``view.redirect()``, which are defined
in the grokked form base classes.

Also note that you can use the view ``@@ploneform-macros`` from 
`plone.app.z3cform`_ if you want to use some of the standard form markup.
For example, the ``titlelessform`` macro will render the ``<form >`` element
and all fieldsets and fields::

    <metal:block use-macro="context/@@ploneform-macros/titlelessform" />

Troubleshooting
---------------

Forms are not found
=====================

When you try to access your form on the site, you'll get page not found (NotFound exception).

* Make sure that you typed your form name correctly and it matches ``grok.name()``
  or lowercased class name
  
* Make sure you have <include package="plone.directives.form" file="meta.zcml" />
  or similar in configure.zcml of your add-on product

.. _five.grok: http://pypi.python.org/pypi/five.grok
.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _plone.z3cform: http://pypi.python.org/pypi/plone.z3cform
.. _plone.app.z3cform: http://pypi.python.org/pypi/plone.app.z3cform
.. _plone.supermodel: http://pypi.python.org/pypi/plone.supermodel
.. _plone.autoform: http://pypi.python.org/pypi/plone.autoform
.. _grokcore.view: http://pypi.python.org/pypi/grokcore.view
