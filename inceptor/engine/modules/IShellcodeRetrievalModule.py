from abc import ABC

from engine.modules.TemplateModule import TemplateModule


class IShellcodeRetrievalModule(TemplateModule, ABC):
    def __init__(self, name, libraries, components, arch, resources=None):
        super().__init__(name=name, libraries=libraries, components=components, arch=arch, resources=resources)
        self.loadable = True

