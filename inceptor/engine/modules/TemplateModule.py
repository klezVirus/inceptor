import os
import re
import traceback
from abc import abstractmethod
from pydoc import locate

from config.Config import Config
from engine.component.TemplateModuleComponent import TemplateModuleComponent
from enums.Architectures import Arch
from enums.Language import Language


class ModuleNotCompatibleException(Exception):
    pass


class ModuleNotLoadableException(Exception):
    pass


class ModuleNotFoundException(Exception):
    pass


class TemplateModule:
    def __init__(self, name: str = None, arch=Arch.x64, libraries: list = None, components: list = None):
        self.components = components if components else []
        self.libraries = libraries if libraries else []
        self.name = name
        self.arch = arch
        self.order = None
        self.compile = False
        self.filter_string = ""
        self.loadable = True

    def add_component(self, component):
        self.components.append(component)

    @abstractmethod
    def generate(self, **kwargs):
        pass

    @abstractmethod
    def build(self, **kwargs):
        pass

    @staticmethod
    def all_modules(init=False):
        kwargs = {
            "language": Language.CSHARP,
            "seconds": 1,
            "dinvoke": True,
            "process": "",
            "pinject": True,
            "arch": Arch.x64
        }
        modules_path = str(Config().get_path("DIRECTORIES", "MODULES"))
        all_files = [
            f for f in
            os.listdir(modules_path)
            if os.path.isfile(os.path.join(modules_path, f))
               and f not in [
                   "TemplateModule.py",
                   "__init__.py",
                   "AdditionalSourceModule.py",
                   "AssemblyInfoModule.py",
                   "EncoderModule.py",
                   "PowerShellModule.py",
               ]
        ]
        module_names = ["_".join(re.sub(r"([A-Z])", r" \1", f.replace("Module.py", "")).split()).lower() for f in
                        all_files]
        if not init:
            return module_names
        return [TemplateModule.from_name(m, kwargs=kwargs) for m in module_names]

    @staticmethod
    def from_name(name, **kwargs):
        try:
            _module_name = "".join([n.capitalize() for n in str(name).split("_")])
            _class_string = f"engine.modules.{_module_name}Module.{_module_name}Module"
            # print(_class_string)
            _class = locate(_class_string)
            _instance = _class(kwargs=kwargs['kwargs'])
            if not _instance.loadable or not hasattr(_instance, "loadable"):
                raise ModuleNotLoadableException()
            return _instance
        except ModuleNotCompatibleException:
            raise ModuleNotCompatibleException()
        except TypeError as e:
            if str(e).find("unexpected keyword argument 'kwargs'") > -1:
                raise ModuleNotLoadableException()
            elif str(e).find("'NoneType' object is not callable") > -1:
                raise ModuleNotFoundException()
            else:
                traceback.print_exc()
        except Exception as e:
            traceback.print_exc()
            pass
