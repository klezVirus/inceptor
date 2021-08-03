import configparser
import os
import traceback
from pathlib import Path

from utils.utils import get_project_root


class Config(object):
    def __init__(self, auto_load: bool = True, create_env: bool = True):
        self.config = configparser.ConfigParser(allow_no_value=True, interpolation=configparser.ExtendedInterpolation())
        self.file = os.path.join(get_project_root(), "config", "config.ini")
        if not os.path.isfile(self.file):
            self.write_default()
        if auto_load:
            self.load_config()
        if create_env:
            self.rebase()

    def load_config(self, filename=None):
        if filename:
            self.file = Path(filename).absolute()
        try:
            self.config.read(self.file)
        except FileNotFoundError:
            print("The file specified does not exists")
            self.write_default()
        except configparser.ParsingError:
            print("Error encountered while parsing, check configuration file syntax")
        except Exception as e:
            print("Unhandled exception, contact support")
            print(f"Exception : {e}")

    def save_config(self):
        with open(self.file, 'w') as configfile:
            self.config.write(configfile)

    def rebase(self):
        no_rebase = ["", "csharp", "cpp", "powershell", "nodebug"]
        for key, directory in self.config["DIRECTORIES"].items():
            if directory and directory not in no_rebase:
                p = Path(os.path.join(get_project_root(), directory))
                p.mkdir(parents=True, exist_ok=True)
        return self

    def get_config(self):
        return self.config

    def get_section(self, s):
        return self.config[s]

    def get_boolean(self, section, key):
        try:
            debug = int(self.get(section, key))
            return debug == 1
        except KeyError:
            return False
        except ValueError:
            return False
        except TypeError:
            return False
        except Exception as e:
            raise e

    def get_int(self, section, key):
        try:
            return int(self.get(section, key))
        except KeyError:
            return False
        except ValueError:
            return False
        except TypeError:
            return False
        except Exception as e:
            raise e

    def get_path(self, section, key):
        try:
            _path = Path(os.path.join(get_project_root(), self.get(section, key))).absolute()
            return _path
        except KeyError:
            return None
        except ValueError:
            return None
        except TypeError:
            return None
        except Exception as e:
            raise e

    def get_list(self, section, key):
        try:
            return [x.strip().encode() for x in self.get(section, key).split(",")]
        except KeyError:
            return None
        except ValueError:
            return None
        except TypeError:
            return None
        except Exception as e:
            raise e

    def get(self, s, v):
        try:
            return self.config[s][v]
        except KeyError:
            return None

    def set(self, s, v, new_value):
        self.config[s][v] = new_value

    def test(self):
        print(self.get("PLACEHOLDERS", "SHELLCODE"))

    def write_default(self):
        with open(self.file, "w") as default:
            default.write(r"""[COMPILERS]
vcvarsall = 
clx86_compiler = 
clx64_compiler = 
masmx86_compiler = 
masmx64_compiler = 
cscx86_compiler = C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe
cscx64_compiler = C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
clangx86_compiler =
clangx64_compiler =
llvmx86_compiler = 
llvmx64_compiler = 
msbuildx86_compiler =
msbuildx64_compiler =
libx64_compiler = 
libx86_compiler = 

[SIGNERS]
signtool_x86 = 
signtool_x64 = 

[DUMPERS]
dumpbin_x86 = 
dumpbin_x64 = 

[DIRECTORIES]
artifacts = artifacts
templates = templates\${MISC:release}
bypass = ${TEMPLATES}\amsi
antidebug = nodebug
powershell = ${TEMPLATES}\powershell
writer = temp
certificates = certs
native = ${TEMPLATES}\cpp
dotnet = ${TEMPLATES}\csharp
test = ${TEMPLATES}\testers
dll = ${TEMPLATES}\cpp\code_execution
obfuscators = obfuscators
syscalls = syscalls
syscalls_x86 = syscalls\syswhispersv2_x86\x86
encoders = encoders\implementations\${MISC:release}
libs = libs\public
modules = engine\modules

[OBFUSCATORS]
powershell = ${DIRECTORIES:obfuscators}\powershell
dotnet = ${DIRECTORIES:obfuscators}\dotnet
native = ${DIRECTORIES:obfuscators}\native

[SIGNING]
domain = www.microsoft.com

[PLACEHOLDERS]
shellcode = ####SHELLCODE####
code = //####CODE####
call = //####CALL####
using = //####USING####
define = //####DEFINE####
bypass = //####BYPASS####
antidebug = //####ANTIDEBUG####
unhook = //####UNHOOK####
args = //####ARGS####
delay = //####DELAY####
find_process = //####FIND_PROCESS####
shellcode_variable = encoded

[SYSCALLS]
syswhispers = 2

[MISC]
logo = 3
bypass_mode = 100
release = public

[DEBUG]
compilers = 0
syswhispers = 0
""")


if __name__ == "__main__":
    c = Config()
    c.test()
