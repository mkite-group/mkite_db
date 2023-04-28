def _named_repr(obj):
    return f"<{obj.__class__.__name__}: {obj.name} ({obj.id})>"
