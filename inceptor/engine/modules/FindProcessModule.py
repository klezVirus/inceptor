import os
import sys

from engine.component.CodeComponent import CodeComponent
from engine.component.FindProcessComponent import FindProcessComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Language import Language
from engine.component.BypassComponent import BypassComponent
from engine.component.DelayComponent import DelayComponent
from utils.console import Console
from utils.utils import get_project_root, static_random_ascii_string


class FindProcessModule(TemplateModule):
    def generate(self, **kwargs):
        pass

    def build(self, **kwargs):
        pass

    def __init__(self, **kwargs):

        language = kwargs["kwargs"]["language"]
        process = kwargs["kwargs"]["process"]
        pinject = kwargs["kwargs"]["pinject"]
        dinvoke = kwargs["kwargs"]["dinvoke"]
        syscalls = kwargs["kwargs"]["syscalls"]

        if dinvoke or syscalls:
            Console.warn_line("[WARNING] Find process still doesn't support syscalls and manual mapping")

        if not pinject:
            Console.auto_line(f"[-] {self.__class__.__name__} requires (-P|--pinject)!")
            sys.exit(1)
        if not process:
            Console.auto_line(f"[-] {self.__class__.__name__} requires (-P0|--process)!")
            sys.exit(1)

        classname = static_random_ascii_string(min_size=3, max_size=10)
        function = static_random_ascii_string(min_size=3, max_size=10)

        if language == Language.CSHARP:
            components = [
                UsingComponent(code=f"System.Diagnostics", language=language),
                CodeComponent(code=fr"""
                    public static class {classname}
                    {{
                        public static int {function}(string processName) {{
                            int pid = Process.GetCurrentProcess().Id;
                            Process[] processes = Process.GetProcessesByName(processName);
                            if (processes.Length > 0) {{
                                pid = processes[0].Id;
                            }}
                            return pid;
                        }}
                    }}
                """),
                FindProcessComponent(code=f'pid = {classname}.{function}("{process}");')
            ]
        elif language == Language.CPP:
            components = [
                UsingComponent(code="<windows.h>", language=language),
                UsingComponent(code="<stdio.h>", language=language),
                UsingComponent(code="<stdlib.h>", language=language),
                UsingComponent(code="<Tlhelp32.h>", language=language),
                UsingComponent(code="<string.h>", language=language),
                CodeComponent(code=fr"""
                    DWORD {function}(const wchar_t* processName);
                    DWORD {function}(const wchar_t* processName) {{
                        PROCESSENTRY32 processInfo;
                        processInfo.dwSize = sizeof(processInfo);
                        HANDLE processesSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);
                        if (processesSnapshot == INVALID_HANDLE_VALUE)
                            return 0;
                        Process32First(processesSnapshot, &processInfo);
                        if (_wcsicmp(processName, processInfo.szExeFile) == 0)
                        {{
                            CloseHandle(processesSnapshot);
                            return processInfo.th32ProcessID;
                        }}
                        while (Process32Next(processesSnapshot, &processInfo))
                        {{
                            if (_wcsicmp(processName, processInfo.szExeFile) == 0)
                            {{
                                CloseHandle(processesSnapshot);
                                return processInfo.th32ProcessID;
                            }}
                        }}
                        CloseHandle(processesSnapshot);
                        return 0;
                    }}
                """),
                FindProcessComponent(code=fr"""
                    const wchar_t* proc = L"{process}.exe";
                    pid = {function}(proc);
                    """)
            ]
        elif language == Language.POWERSHELL:
            components = [
                FindProcessComponent(code=fr"""
                $list = (Get-Process {process})
                if ($list.Length -gt 0){{ 
                    $targetpid = $list[0].Id
                }}
                """)
            ]
        else:
            raise ModuleNotCompatibleException()
        libraries = None
        super().__init__(name="FindProcess", libraries=libraries, components=components)
