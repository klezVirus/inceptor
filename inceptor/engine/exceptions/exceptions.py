class ModuleNotCompatibleException(Exception):
    def __str__(self):
        return self.__class__.__name__


class ModuleLinkingModeException(Exception):
    def __str__(self):
        return self.__class__.__name__


class ModuleNotLoadableException(Exception):
    def __str__(self):
        return self.__class__.__name__


class ModuleNotFoundException(Exception):
    def __str__(self):
        return self.__class__.__name__
