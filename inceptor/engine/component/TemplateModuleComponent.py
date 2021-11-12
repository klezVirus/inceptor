from abc import ABC

from enums.Language import Language


class TemplateModuleComponent(ABC):
    def __init__(self, code=None, placeholder=None, trail=False):
        self.placeholder = placeholder
        self.__code = code
        self.trail = trail

    @property
    def code(self):
        if not self.trail:
            return self.__code
        else:
            return f"{self.__code};\n{self.placeholder}"

    def as_function_call(self, content, language=None):
        pass

    def use_ps_placeholder(self):
        self.placeholder = self.placeholder.replace("/", "")

    def use_raw_placeholder(self):
        self.placeholder = self.placeholder.replace("/", "")

    def use_c_placeholder(self):
        if self.placeholder and self.placeholder[:2] != "//":
            self.placeholder = f"//{self.placeholder}"

    def placeholder_style(self, language=None):
        if not language:
            return
        if language == Language.POWERSHELL:
            self.use_ps_placeholder()
        else:
            self.use_c_placeholder()

