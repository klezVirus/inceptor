from compilers.Compiler import Compiler


class LibCompiler(Compiler):

    def __init__(self, args=None, aargs=None, arch="x64"):
        super().__init__(None, args=args, aargs=aargs, sep=":", arch=arch)

    def default_args(self, outfile):
        self.args = {
            '/OUT': f"\"{outfile}\""
        }

    def add_include_directory(self, directory):
        pass

    def set_libraries(self, libs: list):
        pass

    def set_debug(self):
        pass
