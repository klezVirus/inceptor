from config.Config import Config
from engine.modules.TemplateModule import TemplateModule
from enums.Architectures import Arch


class AdditionalSourceModule(TemplateModule):
    def generate(self, **kwargs):
        content = kwargs["kwargs"]["content"]
        if content:
            with open(self.path, "w") as source:
                source.write(content)

    def build(self, **kwargs):
        pass

    def __init__(self, path, content=None, name=None, arch=Arch.x64):
        libraries = None
        components = None
        self.path = path
        if not name:
            name = "AdditionalSourceModule"
        super().__init__(name=name, libraries=libraries, components=components, arch=arch)

        kwargs = {
            "content": content
        }
        self.generate(kwargs=kwargs)
