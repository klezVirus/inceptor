from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class DelayComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "DELAY")
        super().__init__(code, placeholder)
