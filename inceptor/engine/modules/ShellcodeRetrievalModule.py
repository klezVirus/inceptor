from engine.modules.TemplateModule import TemplateModule


class PowerShellModule(TemplateModule):
    def generate(self, **kwargs):
        pass

    def build(self, **kwargs):
        pass

    def __init__(self, libraries, components):
        super().__init__(name="ShellcodeRetrievalModule", libraries=libraries, components=components)
        self.loadable = False
