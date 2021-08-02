from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class CodeComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "CODE")
        super().__init__(code, placeholder)
