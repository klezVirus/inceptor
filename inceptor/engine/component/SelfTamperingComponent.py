from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class SelfTamperingComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "SELF_TAMPERING")
        super().__init__(code, placeholder)
