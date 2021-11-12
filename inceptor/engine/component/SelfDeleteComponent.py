from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class SelfDeleteComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "SELF_DELETE")
        super().__init__(code, placeholder)
