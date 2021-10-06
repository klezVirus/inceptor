#!/usr/bin/env python
import os
import shutil
import sys
import argparse
import time

from argparse import RawTextHelpFormatter
from encoders.EncoderChain import EncoderChain
from engine.modules.TemplateModule import TemplateModule
from generators.DotNetArtifactGenerator import DotNetArtifactGenerator
from generators.NativeArtifactGenerator import NativeArtifactGenerator
from generators.PowerShellArtifactGenerator import PowerShellArtifactGenerator
from utils.console import Console
from utils.logo import get_logo
from utils.ThreatCheck import ThreatCheck
from utils.utils import isDotNet

HISTORY = "history.txt"


def i_do_not_remember():
    import pandas as pd
    from io import StringIO

    data = """
    Input File Extension,SpecialCondition,Guessed Filetype,Default Loader, Default Template
    .raw,N/A,Shellcode,Simple Loader,Classic
    .exe,.NET,Dotnet Executable,Donut,Classic
    .exe,N/A,Native Executable,Pe2Shellcode,PE Load
    .dll,N/A,Native Library,sRDI,Classic
    """
    df = pd.read_csv(StringIO(data))
    print("[*] Default Loaders")
    print(df)
    print()


def welcome():
    print(get_logo())
    time.sleep(2)


if __name__ == '__main__':
    os.system('color')
    parser = argparse.ArgumentParser(
        description=r"""
inceptor: A Windows-based PE Packing framework designed to help 
          Red Team Operators to bypass common AV and EDR solutions
        """, add_help=True, formatter_class=RawTextHelpFormatter)
    parser.add_argument("-hh", required=False, action='store_true', help="Show functional table")
    parser.add_argument("--list-modules", required=False, action='store_true', help="Show loadable modules")
    parser.add_argument("-Z", "--check", required=False, action='store_true', help="Check file against DefenderCheck")

    subparsers = parser.add_subparsers(help="")
    native_parser = subparsers.add_parser('native', help='Native Artifacts Generator', add_help=True)
    native_parser.set_defaults(which='native')
    native_parser.add_argument(
        '-t', '--transformer', required=False, type=str, choices=["loader", "pe2sh", "donut", "srdi"], default=None,
        help='Compiler arguments')
    native_parser.add_argument(
        '-C', '--compiler', required=False, choices=["cl", "clang", "llvm"], default="cl", help='Compiler to use')
    native_parser.add_argument(
        '-a', '--compiler-args', required=False, type=str, default=None, help='Compiler arguments')
    native_parser.add_argument(
        '--classname', required=False, type=str, default=None, help='Class name <namespace.class> (required for .NET DLLs)')
    native_parser.add_argument(
        '--function', required=False, type=str, default=None, help='Function name (required for DLLs)')
    native_parser.add_argument(
        '--exports', required=False, type=str, default=None, help='Definition file with DLL exported function')
    native_parser.add_argument(
        '-e', '--encoder', action='append', required=False, default=None, help='Encoder(s) to be used')
    native_parser.add_argument(
        '-o', '--outfile', required=True, type=str, default=None, help='Name of the generated Native executable')
    native_parser.add_argument(
        '-m', '--modules', required=False, action='append', default=[],
        help='Modules to use (dinvoke, syscalls, unhook...)')
    native_parser.add_argument(
        '-P', '--pinject', required=False, action='store_true', default=False,
        help='Use a process injection template')
    native_parser.add_argument(
        '-P0', '--process', required=False, type=str, default=False,
        help='Inject into a specific process (Image Name)')
    native_parser.add_argument(
        '--arch', required=False, type=str, choices=["x86", "x64"], default="x64", help='Architecture')
    native_parser.add_argument(
        '--sgn', required=False, default=False, action='store_true', help='Uses Shikata-Ga-Nai as assembly encoder')
    native_parser.add_argument(
        '-p', '--params', required=False, type=str, default=None, help='Params to pass to the wrapped .NET executable')
    native_parser.add_argument(
        '-s', '--sign', required=False, default=False, action='store_true',
        help='Sign the binary (default: CarbonCopy)')
    native_parser.add_argument(
        '-so', '--sign-offline', required=False, default=False, action='store_true',
        help='Sign the binary with LazySign logic')
    native_parser.add_argument(
        '-ss', '--sign-steal', required=False, default=None, type=str,
        help='Sign the binary stealing the signature from another')
    native_parser.add_argument(
        '-sd', '--sign-domain', required=False, default=None, type=str,
        help='Sign the binary dumping the certificate from a domain')
    native_parser.add_argument(
        '-O', '--obfuscate', required=False, action='store_true', default=False,
        help='Obfuscate the native loader (same as -C llvm)')
    native_parser.add_argument(
        '--dll', required=False, default=False, action='store_true', help='If set, generates a wrapper DLL')
    native_parser.add_argument(
        '--clone', required=False, type=str, default=None, help='Clone metadata from another binary')
    native_parser.add_argument(
        '--delay', required=False, default=None, type=int, help='Add a delay of n seconds before execution')
    native_parser.add_argument(
        '-hw', '--hide-window', required=False, action='store_true',
        help='Remove the starting console window when the executable is launched')
    native_parser.add_argument(
        'binary',
        help='Binary file to convert (EXE or RAW for Vanilla Injection)')

    dotnet_parser = subparsers.add_parser('dotnet', help='.NET Artifacts Generator', add_help=True)
    dotnet_parser.set_defaults(which='dotnet')
    dotnet_parser.add_argument(
        '-t', '--transformer', required=False, type=str, choices=["loader", "donut", "pe2sh", "srdi"], default=None,
        help='Shellcode Transformer')
    dotnet_parser.add_argument(
        '-m', '--modules', required=False, action='append', default=[],
        help='Modules to use (dinvoke, syscalls, amsi...)')
    dotnet_parser.add_argument(
        '-O', '--obfuscate', required=False, action='store_true', default=False,
        help='Obfuscate the C# loader')
    dotnet_parser.add_argument(
        '-P', '--pinject', required=False, action='store_true', default=False,
        help='Use a process injection template')
    dotnet_parser.add_argument(
        '-P0', '--process', required=False, type=str, default=False,
        help='Inject into a specific process (Image Name)')
    dotnet_parser.add_argument(
        '-e', '--encoder', action='append', required=False, default=None, help='Encoder(s) to be used')
    dotnet_parser.add_argument(
        '-a', '--compiler-args', required=False, type=str, default=None, help='Compiler arguments')
    dotnet_parser.add_argument(
        '-C', '--compiler', required=False, choices=["csc"], default="csc", help='Compiler to use')
    dotnet_parser.add_argument(
        '-p', '--params', required=False, type=str, default=None, help='Params to pass to the wrapped .NET executable')
    dotnet_parser.add_argument(
        '--classname', required=False, type=str, default=None, help='Class name <namespace.class> (required for .NET DLLs)')
    dotnet_parser.add_argument(
        '--function', required=False, type=str, default=None, help='Function name (required for DLLs)')
    dotnet_parser.add_argument(
        '--arch', required=False, type=str, choices=["x86", "x64", "anycpu", "anycpu-x86", "anycpu-x64"],
        default="x64", help=' Target Architecture')
    dotnet_parser.add_argument(
        '--sgn', required=False, default=False, action='store_true', help='Uses Shikata-Ga-Nai as assembly encoder')
    dotnet_parser.add_argument(
        '-s', '--sign', required=False, default=False, action='store_true', help='Sign the binary (default: CarbonCopy)')
    dotnet_parser.add_argument(
        '-so', '--sign-offline', required=False, default=False, action='store_true',
        help='Sign the binary with LazySign logic')
    dotnet_parser.add_argument(
        '-ss', '--sign-steal', required=False, default=None, type=str,
        help='Sign the binary stealing the signature from another')
    dotnet_parser.add_argument(
        '-sd', '--sign-domain', required=False, default=None, type=str,
        help='Sign the binary dumping the certificate from a domain')
    dotnet_parser.add_argument(
        '-o', '--outfile', required=True, type=str, default=None, help='Name of the generated .NET executable')
    dotnet_parser.add_argument(
        '--clone', required=False, type=str, default=None, help='Clone metadata from another binary')
    dotnet_parser.add_argument(
        '--delay', required=False, default=None, type=int,
        help='Add a delay of n seconds before execution (requires Delay module)')
    dotnet_parser.add_argument(
        '-hw', '--hide-window', required=False, action='store_true',
        help='Remove the starting console window when the executable is launched')
    dotnet_parser.add_argument(
        'binary',
        help='Binary file to convert (exe to perform PE Injection, DLL for RDI and RAW for Vanilla Injection)')

    powershell_parser = subparsers.add_parser('powershell', help='PowerShell Artifacts Generator', add_help=True)
    powershell_parser.set_defaults(which='powershell')
    powershell_parser.add_argument(
        '-m', '--modules', required=False, action='append', default=[],
        help='Modules to use (dinvoke, syscalls, amsi...)')
    powershell_parser.add_argument(
        '-o', '--outfile', required=True, type=str, default=None, help='Name of the generated .NET executable')
    powershell_parser.add_argument(
        '-t', '--transformer', required=False, type=str, choices=["loader", "donut", "pe2sh", "srdi"], default="loader",
        help='Shellcode Transformer')
    powershell_parser.add_argument(
        '-e', '--encoder', action='append', required=False, default=None, help='Encoder(s) to be used')
    powershell_parser.add_argument(
        '--classname', required=False, type=str, default=None, help='Class name <namespace.class> (required for .NET DLLs)')
    powershell_parser.add_argument(
        '--function', required=False, type=str, default=None, help='Function name (required for DLLs)')
    powershell_parser.add_argument(
        '--delay', required=False, default=None, type=int, help='Add a delay of n seconds before execution')
    powershell_parser.add_argument(
        'binary',
        help='Binary file to convert (.NET exe to perform Reflective Loading or RAW for Vanilla Injection)')
    powershell_parser.add_argument(
        '-O', '--obfuscate', required=False, action='store_true', default=False,
        help='Obfuscate the PowerShell Wrapper')
    powershell_parser.add_argument(
        '--arch', required=False, type=str, choices=["x86", "x64"], default="x64",
        help='Architecture')
    powershell_parser.add_argument(
        '--sgn', required=False, default=False, action='store_true', help='Uses Shikata-Ga-Nai as assembly encoder')
    powershell_parser.add_argument(
        '-P', '--pinject', required=False, action='store_true', default=False,
        help='Use a process injection template')
    powershell_parser.add_argument(
        '-P0', '--process', required=False, type=str, default=False,
        help='Inject into a specific process (Image Name)')
    actions = ["native", "dotnet", "powershell"]

    welcome()
    args = parser.parse_args()
    check = False
    start = 2
    if args.hh:
        i_do_not_remember()
        sys.exit(1)
    if args.list_modules:
        for m in TemplateModule.all_modules():
            print(f"  - {m}")
        sys.exit(1)
    if args.check:
        check = True
        start += 1

    action = None
    if len(sys.argv) > 1:
        if sys.argv[1] in actions:
            action = sys.argv[1]
    if len(sys.argv) > 2 and action is None:
        if sys.argv[2] in actions:
            action = sys.argv[2]
    if action is None:
        parser.print_help()
        sys.exit(1)

    filename, ext = os.path.splitext(args.binary)
    filetype = ext.replace(".", "")
    if filetype == "bin":
        Console.warn_line("[WARNING] File extension '.bin' is not supported, assumed '.raw'")
        shutil.copy(args.binary, filename + ".raw")

    binary_abs_path = os.path.abspath(args.binary)
    chain = EncoderChain.from_list(args.encoder)

    if args.process:
        args.modules.append("find_process")
    if args.delay:
        args.modules.append("delay")

    modules = [m.strip() for m in set(args.modules)]

    # Let's record the last command for other uses
    with open(HISTORY, "a") as history:
        history.write(" ".join(sys.argv))

    if filetype == "dll" and isDotNet(binary_abs_path) and not (args.function and args.classname):
        Console.auto_line("[-] .NET DLLs require to specify both class and method names")
        sys.exit(1)

    elif filetype == "dll" and not isDotNet(binary_abs_path) and not args.function:
        Console.auto_line("[-] Native DLLs require to specify an exported function")
        sys.exit(1)

    if action == "native":
        args = native_parser.parse_args(args=sys.argv[start:])
        generator = NativeArtifactGenerator(binary_abs_path,
                                            chain=chain,
                                            outfile=args.outfile,
                                            dll=args.dll,
                                            transformer=args.transformer,
                                            pinject=args.pinject,
                                            process=args.process,
                                            params=args.params,
                                            modules=modules,
                                            sgn=args.sgn,
                                            delay=args.delay,
                                            arch=args.arch,
                                            sign=args.sign,
                                            exports=args.exports,
                                            compiler=args.compiler,
                                            obfuscate=args.obfuscate,
                                            hide_window=args.hide_window,
                                            classname=args.classname,
                                            function=args.function,
                                            clone=args.clone,
                                            domain=args.sign_domain,
                                            offline=args.sign_offline,
                                            steal_from=args.sign_steal
                                            )

    elif action == "dotnet":
        args = dotnet_parser.parse_args(args=sys.argv[start:])
        generator = DotNetArtifactGenerator(file=binary_abs_path,
                                            chain=chain,
                                            outfile=args.outfile,
                                            transformer=args.transformer,
                                            cargs=args.compiler_args,
                                            params=args.params,
                                            modules=modules,
                                            obfuscate=args.obfuscate,
                                            pinject=args.pinject,
                                            process=args.process,
                                            sgn=args.sgn,
                                            delay=args.delay,
                                            arch=args.arch,
                                            sign=args.sign,
                                            hide_window=args.hide_window,
                                            classname=args.classname,
                                            function=args.function,
                                            clone=args.clone,
                                            domain=args.sign_domain,
                                            offline=args.sign_offline,
                                            steal_from=args.sign_steal
                                            )

    elif action == "powershell":
        args = powershell_parser.parse_args(args=sys.argv[start:])
        if filetype not in ["raw", "exe"] or (filetype == "exe" and not isDotNet(binary_abs_path)):
            print("[-] The PowerShell loader can operate on raw shellcode and .NET EXE files only")
            sys.exit(1)
        generator = PowerShellArtifactGenerator(file=binary_abs_path,
                                                chain=chain,
                                                modules=modules,
                                                transformer=args.transformer,
                                                delay=args.delay,
                                                outfile=args.outfile,
                                                sgn=args.sgn,
                                                pinject=args.pinject,
                                                process=args.process,
                                                arch=args.arch,
                                                obfuscate=args.obfuscate,
                                                classname=args.classname,
                                                function=args.function
                                            )
    else:
        raise NotImplementedError(f"[-] Invalid action supplied")

    artifact = generator.generate()

    if check:
        threat_check = ThreatCheck()
        threat_check.check(args.outfile)

