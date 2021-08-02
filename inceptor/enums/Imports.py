import re
from enum import Enum

from enums.Language import Language


class ImportRegex(Enum):
    CSHARP = r"using(\s*[^;]*)\s*;"
    CPP = r'#include(\s*["|<][^"]*[>|"])'
    POWERSHELL = r""

    @staticmethod
    def from_lang(language=None):
        if language == Language.CSHARP:
            return re.compile(ImportRegex.CSHARP.value)
        elif language == Language.CPP:
            return re.compile(ImportRegex.CPP.value)
        else:
            return re.compile(ImportRegex.POWERSHELL.value)
