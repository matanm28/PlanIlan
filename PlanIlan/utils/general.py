from typing import Union, Iterable


def name_of(f: any) -> str:
    name = ''
    if hasattr(f, '__name__'):
        name = f.__name__
    return name


def is_float(value) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def is_real(value: float) -> bool:
    return abs(value) not in (float('inf'), float('nan'))


def is_number(value: Union[int, float, str]) -> bool:
    if isinstance(value, int):
        return True
    elif isinstance(value, float) and is_real(value):
        return True
    elif isinstance(value, str):
        return is_number(value) and is_real(float(value))
    return False


def clean_string(string: str, clean_from: Union[Iterable[str], str]):
    new_string = string
    for c in clean_from:
        new_string = new_string.replace(c, '')
    return new_string
