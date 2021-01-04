def name_of(f: any):
    name = ''
    if hasattr(f, '__name__'):
        name = f.__name__
    return name
