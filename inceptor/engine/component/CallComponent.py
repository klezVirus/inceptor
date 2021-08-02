from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent
from enums.Language import Language


class CallComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDER", "CALL")
        super().__init__(code, placeholder)

    def as_function_call(self, content, language=Language.CSHARP):
        if language == Language.CSHARP:
            return f"{self.code}({content})"
        elif language == Language.CPP:
            return f"{content}\n{self.code}"
        elif language == Language.POWERSHELL:
            return f"({self.code} {content})"
