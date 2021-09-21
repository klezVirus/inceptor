from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class HardcodedArgComponent(TemplateModuleComponent):
    def __init__(self, index, code):
        placeholder = f"####ARG{index}####"
        super().__init__(code, placeholder)
