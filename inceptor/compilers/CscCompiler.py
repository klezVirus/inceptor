from compilers.Compiler import Compiler
from compilers.CompilerExceptions import OperationNotSupported
from config.Config import Config


class CscCompiler(Compiler):

    def add_include_directory(self, directory):
        pass

    def __init__(self, args=None, aargs=None, arch="x64"):
        self.config = Config()
        super().__init__(None, args=args, aargs=aargs, sep=":", arch=arch)
        if not self.args:
            self.args = {}

    def default_exe_args(self, outfile):
        self.args = {
            "/target": "exe",
            "/platform": self.arch,
            "/unsafe": None,
            "/out": f'"{outfile}"'
        }

    def default_dll_args(self, outfile):
        self.args = {
            "/target": "library",
            "/platform": self.arch,
            "/unsafe": None,
            "/out": f'"{outfile}"'
        }
        # "/optimize-": None,

    def hide_window(self):
        if self.args["/target"] == "exe":
            self.args["/target"] = "winexe"
        else:
            raise OperationNotSupported(
                "DLLs don't support hidden windows at compiler level. Consider using SW_HIDE in the template"
            )
        return True

    def set_outfile(self, outfile):
        self.args["/out"] = f'"{outfile}"'

    def set_architecture(self, arch):
        self.args["/platform"] = arch

    def set_libraries(self, libs: list):
        if len(libs) > 0:
            for lib in libs:
                self.args[f'/res:"{lib}"'] = None
            self.args["/r"] = ",".join([f'"{lib}"' for lib in libs])

