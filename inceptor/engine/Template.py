import base64
import os
import re
import traceback
from binascii import hexlify

from config.Config import Config
from encoders.EncoderChain import EncoderChain
from engine.component.ShellcodeRetrievalComponent import ShellcodeRetrievalComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.IShellcodeRetrievalModule import IShellcodeRetrievalModule
from engine.modules.ShellcodeRetrievalModule import ShellcodeRetrievalModule
from engine.modules.AdditionalSourceModule import AdditionalSourceModule
from engine.modules.AssemblyInfoModule import AssemblyInfoModule
from engine.modules.EncoderModule import EncoderModule
from engine.structures.ResourceSet import ResourceSet
from enums.Imports import ImportRegex
from enums.Language import Language


class TemplateException(Exception):
    def __init__(self, message):
        super(TemplateException, self).__init__(message)


class Template:
    def __init__(self, path=None, language=Language.CSHARP, chain: EncoderChain = None, ignore_errors=False):
        self.path = path
        self.imports = []
        self.modules, self.call_decode = chain.translate(language=language) if chain else [], ""
        self.language = language
        self.template = None
        self.shellcode_placeholder = Config().get("PLACEHOLDERS", "SHELLCODE")
        self.call_placeholder = Config().get("PLACEHOLDERS", "CALL")
        if self.language == Language.POWERSHELL:
            self.call_placeholder = self.call_placeholder.replace("/", "")
        self.load_template(path, ignore_errors=ignore_errors)
        self.template_name = os.path.splitext(path)[0].upper().split("\\")[-1]
        self.components = []
        self.libraries = []
        self.defined = []
        self.shellcode_type = bytes
        self.shellcode_retrieval_module: ShellcodeRetrievalModule = None

    def identify_imports(self, raw_template):
        matches = ImportRegex.from_lang(language=self.language).finditer(raw_template, re.MULTILINE)
        for m in matches:
            self.imports.append(m)

    def load_template(self, path, ignore_errors=False):
        if not path or not os.path.isfile(path):
            return
        try:
            with open(path, "r") as template_file:
                raw_template = template_file.read()
        except Exception as e:
            print(f"[-] Exception in load_template while opening template file {path}")
            print(f"[-] Exception: {e}")
            return
        if raw_template.find(self.shellcode_placeholder) < 0 and not ignore_errors:
            raise TemplateException(f"[-] Error: Template missing SHELLCODE placeholder!")
        self.identify_imports(raw_template)
        self.template = base64.b64encode(raw_template.encode())

    def load_chain(self, chain: EncoderChain = None):
        modules = []
        if chain:
            modules, self.call_decode = chain.translate(language=self.language)
            if not chain.is_empty():
                self.shellcode_type = chain.last_element.decoder_in
        self.modules = [m for m in self.modules if not isinstance(m, EncoderModule)] + modules
        self.process_modules()

    def process_modules(self):
        self.libraries = []
        self.components = []
        for module in self.modules:
            if not module:
                continue
            if isinstance(module, IShellcodeRetrievalModule):
                self.shellcode_retrieval_module = module
            if not isinstance(module, EncoderModule) or (
                    isinstance(module, EncoderModule) and module.name not in self.defined
            ):
                self.libraries += module.libraries
                self.components += module.components
                self.defined.append(module.name)
        self.libraries = list(set(self.libraries))

    def collect_sources(self):
        sources = []
        for module in self.modules:
            if isinstance(module, AssemblyInfoModule) or isinstance(module, AdditionalSourceModule):
                sources.append(module.path)
        return sources

    def collect_resources(self):
        resources = ResourceSet()
        for module in self.modules:
            if not hasattr(module, "resources"):
                continue
            if not module.resources:
                continue
            if not module.resources.is_empty():
                resources.append(module.resources)
        return resources

    def add_module(self, module):
        self.modules.append(module)

    @staticmethod
    def fix_size(shellcode):
        return shellcode
        # Originally, shellcode was saved in "\x90" format
        # if len(shellcode) > 65535:
        #     i_am_on_crack = [x for x in shellcode.split("\\x") if x != "" and x != " " and x is not None]
        #     return "{0x" + ', 0x'.join(i_am_on_crack) + "}"
        # elif len(shellcode) > 10000:
        #     rep = [shellcode[i:i + 10000] for i in range(0, len(shellcode), 10000)]
        # else:
        #     rep = [shellcode]
        # return '"\n"'.join(rep)

    def otf_replace(self, placeholder, code):
        raw_template = base64.b64decode(self.template).decode()
        raw_template = raw_template.replace(placeholder, code)
        self.template = base64.b64encode(raw_template.encode())

    def craft(self, shellcode):
        return self.shellcode_retrieval_module.craft(shellcode, language=self.language)

    def clean(self, template):
        new_content = []
        regex = re.compile(r"^\s*//.*$")
        for line in template.split("\n"):
            if not regex.search(line):
                new_content.append(line)
        return "\n".join(new_content)

    def generate(self, shellcode=None):
        raw_template = base64.b64decode(self.template).decode()
        for c in self.components:
            # print(c.placeholder.strip())
            # print(c.code.strip())
            # Is this something we should replace in the main template?
            if not hasattr(c, "placeholder_style"):
                continue
            c.placeholder_style(language=self.language)
            # Avoids duplicating imports
            if isinstance(c, UsingComponent):
                if c.code.strip() in self.imports:
                    continue
            if isinstance(c, ShellcodeRetrievalComponent):
                c.use_raw_placeholder()
                raw_template = raw_template.replace(c.placeholder, c.code)
                raw_template = raw_template.replace("####SHELLCODE_LENGTH####", c.shellcode_length)
            else:
                raw_template = raw_template.replace(c.placeholder, c.code + f"\n{c.placeholder}")
        if shellcode:
            # raw_template = raw_template.replace(self.shellcode_placeholder, self.craft(shellcode))
            raw_template = raw_template.replace(self.call_placeholder, self.call_decode + f"\n{self.call_placeholder}")
        raw_template = self.clean(raw_template)
        return raw_template

    @property
    def content(self):
        return base64.b64decode(self.template).decode()
