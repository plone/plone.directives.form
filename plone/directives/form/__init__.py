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
# ...     form.fieldset('details', label=u"Details", fields=('alpha', 'beta',))
# ...     form.mode(secret_field='hidden',)
# ...     form.order_before(field1='field2')
# ...     form.order_after(field2='field3')
# 
# Here, the 'body' field will use a WYSIWYG widget; 'debug_field' and
# 'extra_info' will be omitted from forms; the fields 'alpha' and 'beta' will
# go into a separate fieldset 'details'; the 'secret_field' field will be
# rendered as a hidden field; and 'field1' will be moved to go before 
# 'field2' and 'field2' will be moved to go after 'field3'.

zope.deferredimport.defineFrom('plone.directives.form.form',
    'omitted', 'mode', 'widget', 'order_before', 'order_after',
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