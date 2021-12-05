from enum import Enum


class LinkingModeNotSelectable(Exception):
    pass


class LinkingMode(Enum):
    SOURCE = 0
    LIBRARY = 1
    ALL = 2

    @staticmethod
    def from_str(label):
        if label.lower() in ["l", "lib", "library"]:
            return LinkingMode.LIBRARY
        elif label.lower() in ["s", "src", "source"]:
            return LinkingMode.SOURCE
        else:
            raise LinkingModeNotSelectable
