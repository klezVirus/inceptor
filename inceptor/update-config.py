import os
import sys
import tempfile
import time
import traceback
import py7zr

from urllib import request
from config.Config import Config
from pathlib import Path

WIN_SDK = "https://developer.microsoft.com/it-it/windows/downloads/windows-10-sdk/"
VS_BT = f"https://visualstudio.microsoft.com/downloads/?utm_medium=microsoft&utm_source=docs.microsoft.com" \
        f"&utm_campaign=navigation+cta&utm_content=download+vs2019"
NET_FW = "https://dotnet.microsoft.com/download/dotnet-framework"

LLVM_LINK = "https://github.com/klezVirus/obfuscator/releases/download/v1.0.0/llvm-clang-v1.0.0.7z"
MinGW_LINK = "https://sourceforge.net/projects/mingw-w64/"


class MissingCriticalDependency(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class MissingNonCriticalDependency(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def report(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\r{percent}% complete")
    sys.stdout.flush()


def download_llvm():
    sys.stdout.write('\r  [*] Fetching LLVM-Obfuscator ...\n')

    destination = tempfile.NamedTemporaryFile(delete=False, dir=tempfile.gettempdir(), suffix=".7z").name
    request.urlretrieve(LLVM_LINK, destination, reporthook=report)
    sys.stdout.write(f"\r  [+] Download complete, saved as {destination}\n")
    sys.stdout.flush()
    return destination


def choose_logo():
    c = Config()
    print("[*] Which logo would you like to see?")
    choice = 4
    choices = ["No logo", "Name-only logo", "Not-so-cool logo", "Original logo"]

    print("[*] Which logo would you like to see?")
    while choice not in range(0, 4):
        for i in range(0, 4):
            print(f"  {i}: {choices[i]}")
        try:
            choice = int(input("  > "))
        except:
            pass
    c.set("MISC", "logo", choice)
    c.save_config()


def detect_base_path():
    known_paths = [
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017\\",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2021\\",
        "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\",
        "C:\\Program Files\\Microsoft Visual Studio\\2017\\",
        "C:\\Program Files\\Microsoft Visual Studio\\2019\\",
        "C:\\Program Files\\Microsoft Visual Studio\\2021\\",
        "C:\\Program Files\\Microsoft Visual Studio\\2022\\"
    ]
    available = [path for path in known_paths if os.path.isdir(path)]
    print(f"[*] Identified multiple VS Installations")
    print(f"[*] Choose the Visual Studio Version:")
    for n, ver in enumerate(available):
        print(f"  {n}: {ver}")
    choice = -1
    while not (0 <= choice < len(available)):
        try:
            choice = int(input("> "))
        except ValueError:
            continue
        except KeyboardInterrupt:
            sys.exit(1)
    return available[choice]

def update_tools(base_path):
    available = [t for t in os.listdir(f"{base_path}\\Community\\VC\\Tools\\MSVC")]
    print(f"[*] Choose the MSVC Tools version:")
    for n, ver in enumerate(available):
        print(f"  {n}: {ver}")
    choice = -1
    while not (0 <= choice < len(available)):
        try:
            choice = int(input("> "))
        except ValueError:
            continue
        except KeyboardInterrupt:
            sys.exit(1)
    return available[choice]



def update_config():
    c = Config()
    base_path = detect_base_path()
    print(base_path)
    tool_ver = update_tools(base_path)
    c.set("COMPILERS", f"TOOLS_VER", str(tool_ver))
    print("[*] Checking requirements")

    if not os.path.isdir(base_path):
        print("[-] Visual Studio not installed")
        os.startfile(VS_BT)
        sys.exit(1)

    if not os.path.isfile(c.get("COMPILERS", "CSCx86_COMPILER")):
        print("[-] .NET Framework not installed")
        os.startfile(NET_FW)
        sys.exit(1)
    else:
        print("[+] .NET Framework is installed")
    try:
        update_compilers(base_path=base_path, config=c, commit=True)
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        pass
    try:
        update_llvm_compiler()
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        pass
    try:
        update_signers()
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        pass
    try:
        update_dumper(base_path=base_path)
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        pass
    try:
        choose_logo()
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        pass
    print("[+] Finished!")

def update_compilers(base_path, config: Config, commit=False):
    c = config
    print("[*] Checking Windows Build Tools")
    versions = {
        "CLx86_COMPILER": [],
        "CLx64_COMPILER": [],
        "MASMx86_COMPILER": [],
        "MASMx64_COMPILER": [],
        "CLANGx86_COMPILER": [],
        "CLANGx64_COMPILER": [],
        "MSBUILDx86_COMPILER": [],
        "MSBUILDx64_COMPILER": [],
        "LIBx86_COMPILER": [],
        "LIBx64_COMPILER": [],
        "VCVARSALL": []
    }
    found = [False] * len(versions.keys())

    for path in Path(base_path).rglob('*.exe'):
        if path.name == "cl.exe" and path.parent.name == "x86" and path.parent.parent.name == "Hostx86":
            c.set("COMPILERS", f"CLx86_COMPILER", str(path))
            print(f"  [+] Located CL.EXE (32-bit) at {path}")
            found[0] = True
            versions["CLx86_COMPILER"].append(str(path))
        elif path.name == "cl.exe" and path.parent.name == "x64" and path.parent.parent.name == "Hostx64":
            c.set("COMPILERS", f"CLx64_COMPILER", str(path))
            print(f"  [+] Located CL.EXE (64-bit) at {path}")
            found[1] = True
            versions["CLx64_COMPILER"].append(str(path))
        elif path.name == "clang-cl.exe" and path.parent.name == "bin" and path.parent.parent.name == "x64":
            c.set("COMPILERS", f"CLANGx64_COMPILER", str(path))
            print(f"  [+] Located CLANG.EXE (64-bit) at {path}")
            found[2] = True
            versions["CLANGx64_COMPILER"].append(str(path))
        elif path.name == "clang-cl.exe" and path.parent.name == "bin" and path.parent.parent.name == "Llvm":
            c.set("COMPILERS", f"CLANGx86_COMPILER", str(path))
            print(f"  [+] Located CLANG.EXE (32-bit) at {path}")
            found[3] = True
            versions["CLANGx86_COMPILER"].append(str(path))
        elif path.name == "ml.exe" and path.parent.name == "x86" and path.parent.parent.name == "Hostx86":
            c.set("COMPILERS", f"MASMx86_COMPILER", str(path))
            print(f"  [+] Located ML.EXE (32-bit) at {path}")
            found[4] = True
            versions["MASMx86_COMPILER"].append(str(path))
        elif path.name == "ml64.exe" and path.parent.name == "x64" and path.parent.parent.name == "Hostx64":
            c.set("COMPILERS", f"MASMx64_COMPILER", str(path))
            print(f"  [+] Located ML64.EXE (64-bit) at {path}")
            found[5] = True
            versions["MASMx64_COMPILER"].append(str(path))
        elif path.name.lower() == "msbuild.exe" and path.parent.name.lower() == "amd64" and path.parent.parent.name.lower() == "bin":
            c.set("COMPILERS", f"MSBUILDx64_COMPILER", str(path))
            print(f"  [+] Located MSBUILD.EXE (64-bit) at {path}")
            found[6] = True
            versions["MSBUILDx86_COMPILER"].append(str(path))
        elif path.name.lower() == "msbuild.exe" and path.parent.name.lower() == "bin":
            c.set("COMPILERS", f"MSBUILDx86_COMPILER", str(path))
            print(f"  [+] Located MSBUILD.EXE (32-bit) at {path}")
            found[7] = True
            versions["MSBUILDx64_COMPILER"].append(str(path))
        elif path.name == "lib.exe" and path.parent.name == "x86" and path.parent.parent.name == "Hostx86":
            c.set("COMPILERS", f"LIBx86_COMPILER", str(path))
            print(f"  [+] Located LIB.EXE (32-bit) at {path}")
            found[8] = True
            versions["LIBx86_COMPILER"].append(str(path))
        elif path.name == "lib.exe" and path.parent.name == "x64" and path.parent.parent.name == "Hostx64":
            c.set("COMPILERS", f"LIBx64_COMPILER", str(path))
            print(f"  [+] Located LIB.EXE (64-bit) at {path}")
            found[9] = True
            versions["LIBx64_COMPILER"].append(str(path))

    for path in Path(base_path).rglob('*.bat'):
        if path.name == "vcvarsall.bat":
            c.set("COMPILERS", f"VCVARSALL", str(path))
            print(f"  [+] Located VCVARSALL utility at {path}")
            found[10] = True
            versions["VCVARSALL"].append(str(path))

    update_section(c, "COMPILERS", versions)
    c.save_config()

    try:
        if not (found[2] or found[3]) and any(found):
            print("[-] Windows Clang compiler not installed. Opening Microsoft Download site...")
            time.sleep(2)
            os.startfile(VS_BT)
            raise MissingNonCriticalDependency
        elif not all(found):
            print("[-] Windows BuildTools not installed. Opening Microsoft Download site...")
            os.startfile(VS_BT)
            raise MissingCriticalDependency
        else:
            print("[+] Windows BuildTools installed")
            c.save_config()
    except MissingCriticalDependency:
        print("[-] Some critical dependencies where found to be missing. Aborting.")
        sys.exit(1)
    except MissingNonCriticalDependency:
        c.save_config()


# print("[-] Windows SDK not installed")
# os.startfile(WIN_SDK)


def update_llvm_compiler(max_recurse=1):
    if max_recurse < 0:
        return
    c = Config()
    print("[*] Checking LLVM Obfuscate Toolchains")
    found = False
    for path in Path(Config().get("OBFUSCATORS", "native")).rglob('*.exe'):
        if path.name == "clang-cl.exe":
            found = True
            print(f"  [+] Located CLANG.EXE (LLVM-Obfuscate) at {path}")
            c.set("COMPILERS", "LLVMx86_COMPILER", str(path.absolute()))
            c.set("COMPILERS", "LLVMx64_COMPILER", str(path.absolute()))
    if found:
        c.save_config()
    else:
        print("[-] LLVM was not found on the system, do you want to download the static binaries?")
        choice = "Q"
        download = False
        while choice.lower() not in ["y", "n"]:
            try:
                choice = input("[Y|N] > ")
                if choice.lower() == "n":
                    download = False
                elif choice.lower() == "y":
                    download = True
            except:
                pass
        if download:
            max_recurse -= 1
            print("[+] Downloading LLVM, the process may take minutes (~500MB)")
            path = download_llvm()
            destination = Config().get_path("OBFUSCATORS", "native").joinpath("llvm-clang")
            destination.mkdir(exist_ok=True, parents=True)

            print(f"[+] Unpacking downloaded file into {str(destination)}")
            with py7zr.SevenZipFile(path, mode='r') as z:
                z.extractall(path=str(destination))
        else:
            print("No Download")
        #update_llvm_compiler(max_recurse=max_recurse)


def update_signers():
    c = Config()
    base_path = "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\"

    print("[*] Checking Windows Code Signing Tools")
    found = [False, False]
    versions = {
        "signtool_x86": [],
        "signtool_x64": []
    }
    for path in Path(base_path).rglob('signtool.exe'):
        if path.parent.name == "x86":
            print(f"  [+] Located signtool x86 utility at {path}")
            found[0] = True
            versions["signtool_x86"].append(str(path))
        elif path.parent.name == "x64":
            print(f"  [+] Located signtool x64 utility at {path}")
            found[1] = True
            versions["signtool_x64"].append(str(path))

    update_section(c, "SIGNERS", versions)
    if not all(found):
        print("[-] Windows Signing Tools not installed")
        os.startfile(WIN_SDK)
        sys.exit(1)
    else:
        print("[+] Windows Signing Tools installed")
        c.save_config()


def update_section(config: Config, section: str, versions: dict):
    if any([True for v in versions.values() if len(v) > 0]):
        for k, v in versions.items():
            if len(v) == 0:
                continue
            if len(v) == 1:
                print(f"[+] Setting {section}.{k} to {v[0]}")
                config.set(section, k, v[0])
                continue
            print(f"[*] Choose a version for {k}:")
            for n, ver in enumerate(v):
                print(f"  {n}: {ver}")
            choice = -1
            while not (0 <= choice < len(v)):
                try:
                    choice = int(input("> "))
                    config.set(section, k, v[choice])
                except ValueError:
                    continue
                except TypeError:
                    continue


def update_dumper(base_path):
    c = Config()

    print("[*] Checking Dumpbin")
    found = [False, False]
    versions = {
        "dumpbin_x86": [],
        "dumpbin_x64": []
    }
    for path in Path(base_path).rglob('dumpbin.exe'):
        if path.parent.name == "x86" and path.parent.name == "x86" and path.parent.parent.name == "Hostx86":
            print(f"  [+] Located dumpbin x86 utility at {path}")
            found[0] = True
            versions["dumpbin_x86"].append(str(path))
        elif path.parent.name == "x64" and path.parent.name == "x64" and path.parent.parent.name == "Hostx64":
            print(f"  [+] Located dumpbin x64 utility at {path}")
            found[1] = True
            versions["dumpbin_x64"].append(str(path))

    update_section(c, "DUMPERS", versions)

    if not all(found):
        print("[-] Windows Dumpbin not installed")
        os.startfile(WIN_SDK)
        sys.exit(1)
    else:
        print("[+] Windows Dumpbin installed")
        c.save_config()


if __name__ == "__main__":
    update_config()
