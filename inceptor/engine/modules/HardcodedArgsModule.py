import os

from engine.component.AntiDebugComponent import AntiDebugComponent
from engine.component.ArgsComponent import ArgsComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DefineComponent import DefineComponent
from engine.component.HardcodedArgComponent import HardcodedArgComponent
from engine.component.TemplateModuleComponent import TemplateModuleComponent
from engine.component.UnookComponent import UnhookComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root


class StaticArgsModule(TemplateModule):
    def generate(self, **kwargs):
        pass

    def build(self, **kwargs):
        pass

    def __init__(self, **kwargs):

        language = kwargs["kwargs"]["language"]
        arch = kwargs["kwargs"]["arch"]
        args = kwargs["kwargs"]["args"]

        if args is None:
            args = []
        libraries = None
        components = []
        for index, arg in enumerate(args, start=1):
            components.append(HardcodedArgComponent(
                index=index,
                code=arg
                ))
        super().__init__(name="HardcodedArgs", libraries=libraries, components=components, arch=arch)
