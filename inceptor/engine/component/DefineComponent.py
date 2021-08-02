import re

from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent
from enums.Language import Language


class DefineComponent(TemplateModuleComponent):
    def __init__(self, code=None, language=Language.CPP):
        placeholder = Config().get("PLACEHOLDERS", "DEFINE")
        super().__init__(code, placeholder)
        self.__code = code
        self.language = language
        self.prefix = ""
        self.suffix = ""

    @property
    def code(self):
        if self.language == Language.CSHARP:
            return f""
        elif self.language == Language.CPP:
            if not self.__code.find("#define") > -1:
                msg = self.prefix + "\n".join([f"#define {c.strip()}" for c in self.__code.split("\n") if len(c.strip()) > 0]) + self.suffix
            else:
                msg = f"{self.prefix}{self.__code}{self.suffix}"
            return msg
        elif self.language == Language.POWERSHELL:
            return f""
        else:
            return self.__code

    def wrap_if_ndef(self):
        self.prefix = "#ifndef\n"
        self.suffix = "#endif\n"
