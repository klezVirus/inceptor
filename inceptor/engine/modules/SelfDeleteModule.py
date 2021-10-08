import os

from engine.component.AntiDebugComponent import AntiDebugComponent
from engine.component.ArgsComponent import ArgsComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DefineComponent import DefineComponent
from engine.component.UnookComponent import UnhookComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root


class SelfDeleteModule(TemplateModule):
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
        components = None
        if language == Language.CPP:
            components = [
                UsingComponent(code="<string.h>", language=language),
                UsingComponent(code="<stdlib.h>", language=language),
                UsingComponent(code="<stdio.h>", language=language),
                CodeComponent(code=r"""
                
                """.replace("####CMDLINE####", "£".join(args))),
                ArgsComponent(code="char** args = get_argv();")
            ]
        elif language == Language.CSHARP:
            ArgsComponent(code=r"""
            
            """.replace("####CMDLINE####", '","'.join(args)))
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="SelfDelete", libraries=libraries, components=components, arch=arch)
