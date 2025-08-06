from django import template
import builtins


register = template.Library()

@register.filter
def map(objects, attr):
    """contoh: {{ list|map:'nilai' }}"""
    results = []
    for obj in objects:
        try:
            for part in attr.split("."):
                obj = getattr(obj, part)() if callable(getattr(obj, part)) else getattr(obj, part)
            results.append(obj)
        except Exception:
            continue
    return results

@register.filter
def average(numbers):
    try:
        numbers = list(numbers)
        return round(sum(numbers) / len(numbers), 2) if numbers else 0
    except:
        return 0

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def split(value, delimiter=","):
    """Memecah string berdasarkan delimiter."""
    return value.split(delimiter)
