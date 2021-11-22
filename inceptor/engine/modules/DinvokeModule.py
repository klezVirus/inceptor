import os
import sys

from config.Config import Config
from engine.component.BypassComponent import BypassComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from utils.utils import get_project_root


class DinvokeModule(TemplateModule):
    def generate(self, **kwargs):
        pass

    def build(self, **kwargs):
        pass

    def __init__(self, **kwargs):
        # Dereference kwargs
        while "kwargs" in kwargs.keys():
            kwargs = kwargs["kwargs"]
        language = kwargs["language"]
        arch = kwargs["arch"]

        self.filter_String = "dinvoke"
        if language == Language.CSHARP:
            components = [
                UsingComponent("DynamicInvoke = DInvoke.DynamicInvoke", language=language)
            ]
            libraries = [str(Config().get_path("DIRECTORIES", "libs").joinpath("DInvoke.dll"))]
            if Config().get("MISC", "release") == "private":
                libraries = [str(Config().get_path("DIRECTORIES", "libs").parent.joinpath("private", arch.value, "DInvoke.dll"))]
        elif language == Language.CPP:
            components = []
            libraries = []
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="Dinvoke", libraries=libraries, components=components)
