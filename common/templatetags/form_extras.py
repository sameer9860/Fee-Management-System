from django import template
from django.forms.boundfield import BoundField

register = template.Library()


@register.filter
def add_class(field, css_class):
    """
    Add CSS class to a form field widget.

    Usage in template:
    {{ form.field_name|add_class:"form-control" }}
    {{ form.field_name|add_class:"form-control mb-3" }}

    Args:
        field: Django form field (BoundField)
        css_class: String of CSS classes to add

    Returns:
        Field with added CSS classes
    """
    if not isinstance(field, BoundField):
        return field

    # Get existing classes from the widget
    existing_classes = field.field.widget.attrs.get("class", "")

    # Combine existing classes with new ones
    if existing_classes:
        new_classes = f"{existing_classes} {css_class}"
    else:
        new_classes = css_class

    # Create a copy of the field to avoid modifying the original
    field_copy = field
    field_copy.field.widget.attrs["class"] = new_classes

    return field_copy
