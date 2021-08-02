from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class AntiDebugComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "ANTIDEBUG")
        super().__init__(code, placeholder)
