import os
import shutil
import sys
import traceback

from config.Config import Config
from engine.TemplateFactory import TemplateFactory
from engine.component.BypassComponent import BypassComponent
from engine.component.UsingComponent import UsingComponent
from engine.enums.Enums import LinkingMode
from engine.modules.AdditionalSourceModule import AdditionalSourceModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from utils.utils import get_project_root


class DinvokeModule(TemplateModule):
    def generate(self, **kwargs):
        language = kwargs["language"]
        path = TemplateFactory.get_module_templates_path(self, language=language)
        mapping = TemplateFactory.map_directory(path)
        for path, temp in mapping.items():
            # print(f"{path}:{temp}")
            shutil.copy2(path, temp)
        return mapping.values()

    def build(self, **kwargs):
        pass

    def __init__(self, **kwargs):
        # Dereference kwargs
        while "kwargs" in kwargs.keys():
            kwargs = kwargs["kwargs"]
        language = kwargs["language"]
        arch = kwargs["arch"]

        linking_mode = LinkingMode.LIBRARY
        sources = []
        if "linking_mode" in kwargs.keys():
            linking_mode = kwargs["linking_mode"]

        self.filter_String = "dinvoke"
        if language == Language.CSHARP and linking_mode == LinkingMode.LIBRARY:
            components = [
                # UsingComponent("DynamicInvoke = DInvoke.DynamicInvoke", language=language),
                UsingComponent("DInvoke", language=language)
            ]
            libraries = [str(Config().get_path("DIRECTORIES", "libs").joinpath("DInvoke.dll"))]
            if Config().get("MISC", "release") == "private":
                libraries = [str(Config().get_path("DIRECTORIES", "libs").parent.joinpath("private", arch.value, "DInvoke.dll"))]
        elif language == Language.CSHARP and linking_mode == LinkingMode.SOURCE:

            sources = self.generate(**kwargs)
            components = [
                UsingComponent("DInvoke", language=language)
            ]
            libraries = []
        elif language == Language.CPP:
            components = []
            libraries = []
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="Dinvoke", libraries=libraries, components=components)
        for source in sources:
            self.additional_modules.append(AdditionalSourceModule(content=None, path=source))
