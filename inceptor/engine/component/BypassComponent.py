from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class BypassComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "BYPASS")
        super().__init__(code, placeholder)
