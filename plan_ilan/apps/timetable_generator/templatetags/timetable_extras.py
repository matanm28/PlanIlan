from collections import Iterable

from django import template

register = template.Library()


@register.filter(name='has_common_items')
def has_common_items(l1: Iterable, l2: Iterable) -> bool:
    return len(set(l1).intersection(l2)) > 0
