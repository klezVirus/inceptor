#!/usr/bin/env python
import os
import subprocess
import sys
import argparse
import secrets
import tempfile
import time
from pathlib import Path

from compilers.ClCompiler import ClCompiler
from compilers.CscCompiler import CscCompiler
from config.Config import Config
from converters.Loader import Loader
from encoders.EncoderChain import EncoderChain
from engine.CodeWriter import CodeWriter
from engine.component.TemplateModuleComponent import TemplateModuleComponent
from engine.modules.TemplateModule import TemplateModule
from enums.Language import Language
from generators.DotNetArtifactGenerator import DotNetArtifactGenerator
from generators.NativeArtifactGenerator import NativeArtifactGenerator
from generators.PowerShellArtifactGenerator import PowerShellArtifactGenerator
from utils.utils import isDotNet, get_project_root


def clean(files):
    for file in files:
        try:
            os.unlink(file)
        except:
            pass
    base_paths = [get_project_root(), os.path.join(get_project_root(), "temp")]
    wildcards = ["*.obj", "*.exp", "*.lib", "*.pdb", "*.shc.exe", "*.bin", "*.raw"]
    for base_path in base_paths:
        for wildcard in wildcards:
            cmd = f"del /F /Q \"{os.path.join(base_path, wildcard)}\""
            subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == '__main__':
    os.system('color')
    parser = argparse.ArgumentParser(description='chain-validate: inceptor chain validator', add_help=True)
    parser.add_argument(
        '-l', '--lang', required=True, type=str, action="append", choices=["cpp", "cs", "ps"], default=None,
        help='Language')
    parser.add_argument(
        '-e', '--encoder', action='append', required=True, default=None, help='Encoder(s) to be used')

    args = parser.parse_args()
    chain = EncoderChain.from_list(args.encoder)

    shellcode = secrets.token_bytes(64)

    languages = [Language.CPP, Language.CSHARP, Language.POWERSHELL]

    if args.lang:
        languages = []
        for lang in args.lang:
            languages.append(Language.from_string(label=lang))
    outfiles = []
    for lang in languages:
        outfile = tempfile.NamedTemporaryFile(dir=Config().get_path("DIRECTORIES", "WRITER"), suffix=".bin",
                                              delete=False).name
        outfiles.append(outfile)
        print(f"[*] Validating encoder chain for {lang.name}")
        if not chain.validate(language=lang):
            print("[-] Failed to validate chain")
            continue
        template_dir = Config().get_path("DIRECTORIES", "TEST")
        c_outfile = outfile.replace("\\", "\\\\")
        compiler = None
        compiled_file = tempfile.NamedTemporaryFile(suffix=".exe", delete=False).name
        if lang == Language.CPP:
            f_component = TemplateModuleComponent(placeholder="####FILE####", code=f"\"{c_outfile}\";", trail=False)
            compiler = ClCompiler()
            compiler.default_exe_args(outfile=compiled_file)
            template_path = template_dir.joinpath("test.cpp")
            f_component.use_c_placeholder()
        elif lang == Language.CSHARP:
            f_component = TemplateModuleComponent(placeholder="####FILE####", code=f"\"{c_outfile}\";")
            compiler = CscCompiler()
            compiler.default_exe_args(outfile=compiled_file)
            template_path = template_dir.joinpath("test.cs")
        else:
            f_component = TemplateModuleComponent(placeholder="####FILE####", code=f"\"{c_outfile}\";")
            template_path = template_dir.joinpath("test.ps1")
            f_component.use_ps_placeholder()
        writer = CodeWriter(template=str(template_path.absolute()), language=lang, modules=[], shellcode=shellcode)
        writer.template.add_module(TemplateModule(name="FileModule", components=[f_component]))
        writer.load_chain(chain=chain)
        encoded = chain.encode(shellcode)
        writer.write_source(shellcode=encoded)
        if compiler:
            compiler.set_libraries(libs=writer.template.libraries)
            compiler.compile([writer.outfile])
        else:
            compiled_file = writer.outfile
        if not os.path.isfile(compiled_file):
            print("[-] Error generating encoder file")
            sys.exit(1)
        loader = Loader()
        cmd = compiled_file
        if lang == Language.POWERSHELL:
            cmd = f"powershell .\\temp\\{Path(compiled_file).name}"
        time.sleep(2)
        try:
            output = subprocess.check_output(f"{cmd}")
        except subprocess.CalledProcessError:
            print("[-] Failed to execute test")
            sys.exit(1)
        if not os.path.isfile(outfile):
            raise FileNotFoundError("Error generating test file")

        transformed = loader.transform(outfile)
        if shellcode == transformed:
            print("[+] Encoder chain working!")
            writer.clean()
        elif shellcode in transformed:
            print("[!] Warning, identified garbage at the end of the transformed shellcode")
            print("[+] Encoder chain working!")
            writer.clean()
        else:
            print("[-] Encoder chain broken!")
            print(f"  [*] File: {loader.transform(outfile)}")
            print(f"  [*] Shellcode: {shellcode}")

        clean([compiled_file] + outfiles)
