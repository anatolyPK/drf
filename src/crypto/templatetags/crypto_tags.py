from django import template


register = template.Library()


@register.filter(name='add_plus_or_minus')
def add_plus_or_minus(value):
    if isinstance(value, (int, float)):
        if value > 0:
            return f'+{value}'
    return value
