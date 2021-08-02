from engine.component.CallComponent import CallComponent
from engine.modules.TemplateModule import TemplateModule
from enums.Architectures import Arch


class EncoderModule(TemplateModule):
    def generate(self, **kwargs):
        pass

    def build(self, **kwargs):
        pass

    def __init__(self, name=None, libraries=None, components=None, call_component: CallComponent = None, arch=Arch.x64):
        super().__init__(name=name, libraries=libraries, components=components, arch=arch)
        self.call_component: CallComponent = call_component
        self.filter_string = ""
