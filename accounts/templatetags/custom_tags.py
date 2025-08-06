from django import template

register = template.Library()

@register.filter
def map(objects, attr):
    """
    Gunakan: {{ orders|map:"items.count"|sum }}
    Mendapatkan nilai dari nested attribute.
    """
    results = []
    for obj in objects:
        try:
            # Mendukung nested: "items.count"
            for part in attr.split("."):
                obj = getattr(obj, part)() if callable(getattr(obj, part)) else getattr(obj, part)
            results.append(obj)
        except Exception:
            continue
    return results

@register.filter
def sum(values):
    try:
        return builtins.sum(values)
    except Exception:
        return 0

# Tambahkan jika belum
import builtins
