from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class UnhookComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "UNHOOK")
        super().__init__(code, placeholder)
