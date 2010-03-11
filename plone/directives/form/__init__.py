#
# Convenience API
#

import zope.deferredimport

# Base class for custom schema interfaces and grok directive to specify a model
# file. For example:
#
# >>> class IMyType(form.Schema)
# ...     form.model('myschema.xml')

zope.deferredimport.defineFrom('plone.directives.form.schema',
    'Schema', 'model', 'fieldset',
)

# Further directives for Schema to influence form rendering. For example:
# 
# >>> class IMyType(form.Schema)
# ...     form.model('myschema.xml')
# ...     form.widget(body='plone.app.z3cform.wysiwyg.WysiwygFieldWidget',)
# ...     form.omitted('debug_field', 'extra_info',)
# ...     form.no_omit(IEditForm, 'debug_field', 'extra_info',)
# ...     form.fieldset('details', label=u"Details", fields=('alpha', 'beta',))
# ...     form.mode(secret_field='hidden',)
# ...     form.order_before(field1='field2')
# ...     form.order_after(field2='field3')
# ...     form.read_permission(field1='zope2.View')
# ...     form.write_permission(field2='cmf.ModifyPortalContent')
# ...     form.primary('field3')
# 
# Here, the 'body' field will use a WYSIWYG widget; 'debug_field' and
# 'extra_info' will be omitted from forms, except for form providing IEditForm;
# the fields 'alpha' and 'beta' will go into a separate fieldset 'details';
# the 'secret_field' field will be rendered as a hidden field; 'field1' will
# be moved to go before 'field2' and 'field2' will be moved to go after
# 'field3'; field1 will only be displayed on a display form or view if the user
# has the 'zope2.View' permission; field2 will only be displayed on an input
# form if the user has the 'cmf.ModifyPortalContent' permission; and 'field3'
# will be marked as a primary field for marshaling purposes

zope.deferredimport.defineFrom('plone.directives.form.schema',
    'omitted', 'no_omit', 'mode', 'widget', 'order_before', 'order_after',
    'read_permission', 'write_permission', 'primary',
)

# Behavior interfaces can either be marked with or be adaptable to this
# interface, in order to provide fields for the standard forms. For example:
# 
# >>> class IMyBehavior(form.Schema):
# ...     form.order_before(enabled='description')
# ...     form.fieldset('tagging', label=u"Tagging", fields=['enabled', 'tags'])
# ...     
# ...     enabled = schema.Bool(title=u"Tagging enabled", default=True)
# ...     
# ...     tags = schema.List(title=u"Tags",
# ...                        value_type=schema.Choice(values=["Tag 1", "Tag 2", "Tag 3"]))
# ... 
# >>> alsoProvides(ITagging, form.IFormFieldProvider)
# 
# When this behavior (and its associated factory) is registered, any type
# where the behavior (that uses the standard Dexterity form support) is 
# enabled will have the appropriate form fields inserted.

zope.deferredimport.defineFrom('plone.autoform.interfaces',
    'IFormFieldProvider',
)

# z3c.form base classes: Form, SchemaForm, AddForm, SchemaAddForm, EditForm,
# SchemaEditForm, DisplayForm. The 'Schema' versions use
# plone.autoform.form.AutoExtensibleForm and require that a schema
# is set using the 'schema' attribute. The other forms are normal forms.
#
# >>> class MyForm(form.Form)
# ...     grok.name('my-form')
# ...     grok.context(IMyContext)
# ...     grok.require('zope2.View')

zope.deferredimport.defineFrom('plone.directives.form.form',
    'Form', 'SchemaForm', 'AddForm', 'SchemaAddForm',
        'EditForm', 'SchemaEditForm', 'DisplayForm',
        'wrap',
)

# z3c.form value adapters for computed values: default_value (for a widget),
# widget_label and button_label.
# 
# >>> @default_value(field=IMySchema['some_field'])
# ... def get_default(data):
# ...     return data.context.Title().lower()
# 
# See docstrings in value.py for more.

zope.deferredimport.defineFrom('plone.directives.form.value',
    'default_value', 'widget_label', 'button_label',
)

# z3c.form widget validator adapters
# 
# >>> @validator(field=IMySchema['some_field'])
# ... def validateField(value):
# ...     if value == 42:
# ...         raise Invalid(u"We don't like this number")

zope.deferredimport.defineFrom('plone.directives.form.validator',
    'validator',
)

# z3c.form error message computed value adapters
# 
# >>> @error_message(error=TooSmall, field=IMySchema['some_field'])
# ... def errorMessage(value):
# ...     return u"The given value (%d) is too small" % value

zope.deferredimport.defineFrom('plone.directives.form.error',
    'error_message',
)
