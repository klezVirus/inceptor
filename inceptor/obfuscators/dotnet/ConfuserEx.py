import os
import subprocess
import tempfile
import traceback

from config.Config import Config
from obfuscators.Obfuscator import Obfuscator, MissingArgumentException
from utils.console import Console
from utils.utils import get_project_root


class ConfuserEx(Obfuscator):
    def __init__(self, **kwargs):
        super().__init__(sep=" ", path=None, args={})
        self.config = Config()
        self.path = os.path.join(get_project_root(), self.config.get("OBFUSCATORS", "dotnet"), self.name,
                                 f"Confuser.CLI.exe")

        if "filename" not in kwargs['kwargs'].keys():
            raise MissingArgumentException("A file to obfuscate is required")
        self.filename = kwargs['kwargs']["filename"]
        self.project_file = self.write_template()

        self.args = {
            "-n": f'"{self.project_file}"'
        }

        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"[-] Missing {self.name} obfuscator utility file")

        if not os.path.isfile(self.filename):
            raise FileNotFoundError(f"[-] Missing {self.name} obfuscator target file")

    def obfuscate(self):
        try:
            Console.auto_line("  [>] Obfuscating...")
            cmd = f"\"{self.path}\" {self.normalise_args()}"
            if self.debug:
                print(cmd)
            subprocess.check_call(
                cmd,
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL
            )
            out_filename = f"{self.filename}"
            Console.auto_line(f"  [>] Obfuscated filename: {out_filename}")
        except subprocess.CalledProcessError:
            traceback.print_exc()
            Console.auto_line(f"[-] Failed to obfuscate payload with {self.name}")
        return None

    def write_template(self):
        temp_dir = str(self.config.get_path('DIRECTORIES', 'WRITER'))
        project_file = tempfile.NamedTemporaryFile(
            delete=True,
            dir=temp_dir,
            suffix=".crproj"
        ).name
        template = rf"""<?xml version="1.0" encoding="utf-8"?>
<project baseDir="{temp_dir}" outputDir="{temp_dir}" xmlns="http://confuser.codeplex.com">
    <rule preset="none" pattern="true">
        <protection id="ctrl flow" />
        <protection id="ref proxy" />
        <protection id="invalid metadata" />
        <protection id="anti debug" />
        <protection id="anti dump" />
        <protection id="anti ildasm" />
        <protection id="anti tamper" />
        <protection id="constants" />
        <protection id="resources" />
    </rule>
    <module path="{self.filename}" />
    <probePath>{temp_dir}</probePath>
</project>
        """
        with open(project_file, "w") as project:
            project.write(template)
        return project_file

#
#
#
#
#
#
#
