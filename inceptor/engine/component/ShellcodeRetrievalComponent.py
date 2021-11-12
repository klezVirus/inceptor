from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent


class ShellcodeRetrievalComponent(TemplateModuleComponent):
    def __init__(self, code=None, shellcode_length=0):
        placeholder = Config().get("PLACEHOLDERS", "SHELLCODE")
        super().__init__(code, placeholder)
        self.shellcode_length = str(shellcode_length)
