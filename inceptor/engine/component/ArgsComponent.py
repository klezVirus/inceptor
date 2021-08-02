from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class ArgsComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "ARGS")
        super().__init__(code, placeholder)
