import re

from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent
from enums.Language import Language


class UsingComponent(TemplateModuleComponent):
    def __init__(self, code=None, language=Language.CSHARP):
        placeholder = Config().get("PLACEHOLDERS", "USING")
        super().__init__(code, placeholder)
        self.__code = code
        self.language = language

    @property
    def code(self):
        if self.language == Language.CSHARP:
            return f"using {self.__code};"
        elif self.language == Language.CPP:
            return f"#include {self.__code}"
        elif self.language == Language.POWERSHELL:
            if re.search(r"^(http|ftp)", self.__code):
                return f'iex (([System.Net.WebClient]::new()).DownloadString("{self.__code}"));'
            else:
                return f'iex ([System.IO.File]::ReadAllBytes("{self.__code}"));'
        else:
            return self.__code
