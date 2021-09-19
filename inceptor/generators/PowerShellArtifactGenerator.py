import shutil
from datetime import datetime
import os

from converters.TransformerFactory import TransformerFactory
from engine.CodeWriter import CodeWriter
from enums.Language import Language
from generators.Generator import Generator
from obfuscators.powershell.Karmaleon import Karmaleon
from utils.console import Console
from utils.utils import sgn


class PowerShellArtifactGenerator(Generator):
    def __init__(self,
                 file,
                 chain=None,
                 outfile=None,
                 delay=None,
                 transformer=None,
                 arch: str = None,
                 sgn: bool = False,
                 pinject: bool = False,
                 process: str = None,
                 classname: str = None,
                 params: str = None,
                 function: str = None,
                 obfuscate: bool = False,
                 modules: list = None
                 ):
        super().__init__(file, chain=chain)
        self.outfile = outfile
        self.obfuscate = obfuscate
        self.sgn = sgn
        self.arch = arch
        self.pinject = pinject
        self.process = process

        if transformer:
            self.transformer = TransformerFactory.from_name(transformer)
        else:
            self.transformer = TransformerFactory.from_file(self.file)

        # If the loader is sRDI, we'll need a class / function to convert
        kwargs = {"classname": classname, "function": function}
        self.transformer.set_additional_arguments(kwargs={**kwargs})

        self.need_parameter_module = False
        try:
            self.transformer.add_parameters(params=params)
        except:
            # print(f"[-] Warning: Transformer {self.transformer.__class__.__name__} does not support parameters")
            self.need_parameter_module = True

        self.writer = CodeWriter(
            file=file,
            modules=modules,
            delay=delay,
            converter=self.transformer,
            language=Language.POWERSHELL,
            pinject=self.pinject,
            process=self.process,
            arch=arch
            )
        self.writer.load_chain(chain=chain)

    def obfuscate_wrapper(self):
        karmaleon = Karmaleon(filename=self.writer.outfile, outfile=self.writer.outfile)
        karmaleon.obfuscate()

    def generate(self):
        step = 0
        Console.auto_line(f"[+] PowerShell Artifact Generator Started At {datetime.utcnow()}")
        Console.auto_line(f"[*] Phase {step}: Loading...")
        step += 1
        if not self.chain.validate(language=Language.POWERSHELL):
            Console.auto_line("\n[-] ERROR: Failed to validate encoding chain")
            return

        Console.auto_line(f"[*] Phase {step}: Converting binary into shellcode")
        step += 1
        shellcode = self.transformer.transform(target=self.file)
        Console.auto_line(f"[*] Phase {step}: Encoding")
        step += 1
        substep = 1
        if self.sgn:
            Console.auto_line(f"  [>] Phase {step}.{substep}: Using Shikata-Ga-Nai {self.arch} to encode the shellcode")
            shellcode = sgn(shellcode, arch=self.arch)
        if not self.chain.is_empty():
            substep += 1
            Console.auto_line(f"  [>] Phase {step}.{substep}: Using Inceptor chained encoder to encode the shellcode")
            Console.auto_line(f"  [>] Encoder Chain: {self.chain.to_string()}")
            shellcode = self.chain.encode(shellcode)
        Console.auto_line(f"[*] Phase 3: Generating wrapper using {self.writer.template.template_name}")
        self.writer.write_source(shellcode=shellcode)
        if self.obfuscate:
            Console.auto_line(f"[*] Phase 4: Obfuscating PowerShell Wrapper")
            self.obfuscate_wrapper()

        if os.path.isfile(self.writer.outfile):
            Console.auto_line(f"  [>] PowerShell wrapper stored at {self.writer.outfile}")
            if self.outfile:
                shutil.copy(self.writer.outfile, self.outfile)
                if os.path.isfile(self.outfile):
                    Console.auto_line(f"  [>] PowerShell wrapper copied to {self.outfile}")
                os.unlink(self.writer.outfile)
        else:
            Console.auto_line("  [-] Error generating PowerShell Wrapper")
        Console.auto_line(f"[+] PowerShell Artifact Generator Finished At {datetime.utcnow()}")
        return self.outfile
