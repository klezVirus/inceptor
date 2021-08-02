from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class FindProcessComponent(TemplateModuleComponent):
    def __init__(self, code=None):
        placeholder = Config().get("PLACEHOLDERS", "FIND_PROCESS")
        super().__init__(code, placeholder)
