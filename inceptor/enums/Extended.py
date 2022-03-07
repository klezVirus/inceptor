from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def get_name(cls, value):
        if isinstance(value, str):
            value = int(value)
        _types = dict(map(lambda c: (c.value, c.name.lower()), cls))
        return _types[value] if value in _types.keys() else None

    @classmethod
    def from_name(cls, name):
        _types = dict(map(lambda c: (c.name.lower(), c.value), cls))
        return _types[name] if name in _types.keys() else None

    @classmethod
    def value_list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def key_list(cls):
        return list(map(lambda c: c.name.lower(), cls))
