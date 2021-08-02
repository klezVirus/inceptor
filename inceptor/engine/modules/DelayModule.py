import os
import sys

from engine.component.BypassComponent import BypassComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DelayComponent import DelayComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from utils.console import Console
from utils.utils import get_project_root


class DelayModule(TemplateModule):
    def generate(self, **kwargs):
        pass

    def build(self, **kwargs):
        pass

    def __init__(self, **kwargs):

        language = kwargs["kwargs"]["language"]
        seconds = kwargs["kwargs"]["seconds"]
        if not seconds or seconds == 0:
            Console.auto_line(f"[-] {self.__class__.__name__} requires --dinvoke!")
            sys.exit(1)

        if language == Language.CSHARP:
            components = [
                DelayComponent(code=f"System.Threading.Thread.Sleep({seconds}*1000);")
            ]
        elif language == Language.CPP:
            components = [
                DelayComponent(code=f"Sleep({seconds}*1000);")
            ]
        elif language == Language.POWERSHELL:
            components = [
                DelayComponent(code=f"sleep {seconds}")
            ]
        else:
            raise ModuleNotCompatibleException()
        libraries = None
        super().__init__(name="Delay", libraries=libraries, components=components)
