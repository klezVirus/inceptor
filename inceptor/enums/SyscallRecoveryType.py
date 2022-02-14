from enums.Extended import ExtendedEnum


class SyscallRecoveryType(ExtendedEnum):
    EMBEDDED = 0
    EGG_HUNTER = 1
    JUMPER = 2
    JUMPER_RANDOMIZED = 3

    @classmethod
    def from_name_or_default(cls, name):
        _types = dict(map(lambda c: (c.name.lower(), c.value), cls))
        return _types[name] if name in _types.keys() else SyscallRecoveryType.EMBEDDED

