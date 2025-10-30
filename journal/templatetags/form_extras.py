from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):

    existing_classes = field.field.widget.attrs.get('class', '')
    field.field.widget.attrs['class'] = f'{existing_classes} {css}'.strip()
    return field

@register.filter(name='add_placeholder')
def add_placeholder(field, text):

    field.field.widget.attrs['placeholder'] = text
    return field

@register.filter(name='add_attr')
def add_attr(field, args):

    for pair in args.split(','):
        if ':' in pair:
            key, value = pair.split(':', 1)
            field.field.widget.attrs[key.strip()] = value.strip()
    return field
