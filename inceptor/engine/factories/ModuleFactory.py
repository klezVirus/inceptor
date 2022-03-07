from engine.exceptions.exceptions import ModuleNotCompatibleException, ModuleNotLoadableException, \
    ModuleNotFoundException
from engine.modules.TemplateModule import TemplateModule
from utils.console import Console


class ModuleFactory:

    @staticmethod
    def from_name(name, **kwargs):
        try:
            return TemplateModule.from_name(
                    name=name,
                    **kwargs
                )
        except ModuleNotCompatibleException as e:
            Console.fail_line(f"[ERROR] Module {name} could not be loaded for {e}")
        except ModuleNotLoadableException as e:
            Console.fail_line(f"[ERROR] Module {name} is not loadable for {e}")
        except ModuleNotFoundException as e:
            Console.fail_line(f"[ERROR] Module {name} was not found for {e}")
        except Exception as e:
            Console.fail_line(f"[ERROR] Module {name} was not found for {e}")
