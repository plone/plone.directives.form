"""This module remains only for BBB."""

from zope.interface.interface import TAGGED_DATA
TEMP_KEY = '__form_directive_values__'


class FormMetadataDictStorage(object):
    """Store a dict value in the TEMP_KEY tagged value, under the key in
    directive.key
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(TAGGED_DATA, {}).setdefault(TEMP_KEY, {})
        tags.setdefault(directive.key, {}).update(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(
            TEMP_KEY, {}).get(directive.key, default)

    def setattr(self, context, directive, value):
        tags = context.queryTaggedValue(TEMP_KEY, {})
        tags.setdefault(directive.key, {}).update(value)


class FormMetadataListStorage(object):
    """Store a list value in the TEMP_KEY tagged value, under the key in
    directive.key
    """

    def set(self, locals_, directive, value):
        tags = locals_.setdefault(TAGGED_DATA, {}).setdefault(TEMP_KEY, {})
        tags.setdefault(directive.key, []).extend(value)

    def get(self, directive, component, default):
        return component.queryTaggedValue(
            TEMP_KEY, {}).get(directive.key, default)

    def setattr(self, context, directive, value):
        tags = context.queryTaggedValue(TEMP_KEY, {})
        tags.setdefault(directive.key, []).extend(value)
