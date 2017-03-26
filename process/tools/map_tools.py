def tag(entity,name):
    return entity.tags[name] if (name in entity.tags) else None