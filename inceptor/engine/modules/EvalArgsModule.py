import os

from engine.component.AntiDebugComponent import AntiDebugComponent
from engine.component.ArgsComponent import ArgsComponent
from engine.component.CodeComponent import CodeComponent
from engine.component.DefineComponent import DefineComponent
from engine.component.UnookComponent import UnhookComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root


class EvalArgsModule(TemplateModule):
    def generate(self, **kwargs):
        pass

    def build(self, **kwargs):
        pass

    def __init__(self, **kwargs):
        libraries = None
        components = None

        language = kwargs["kwargs"]["language"]
        arch = kwargs["kwargs"]["arch"]

        if language == Language.CPP:
            components = [
                UsingComponent(code="<string.h>", language=language),
                UsingComponent(code="<stdlib.h>", language=language),
                UsingComponent(code="<stdio.h>", language=language),
                UsingComponent(code="<processenv.h>", language=language),
                CodeComponent(code=r"""
                size_t size_strar(char ** str_ar);
                char** strsplit(char * str, char delim);
                void free_strar(char ** str_ar);
                size_t size_strar(char ** str_ar) {
                  size_t count = 0;
                  for (int i = 0 ; str_ar[i][0] != '\0' ; i++) {
                    count++;
                  }
                  return count;
                }
                char** strsplit(char * str, char delim) {
                  char** strres;
                  size_t count = 0;
                
                  for (int i = 0 ; i < strlen(str) ; i++) {
                    if (str[i] == delim || str[i] == '\n' || str[i] == '\0')
                      count++;
                  }
                  strres = (char**)malloc(++count * sizeof *strres);
                
                  char buffer[100]; int actual = 0, place = 0;
                  for (int i = 0 ; i < strlen(str) ; i++) {
                    if (str[i] != delim && str[i] != '\n' && str[i] != '\0') {
                      buffer[actual++] = str[i];
                    }
                    else {
                      buffer[actual] = '\0';
                      actual = 0;
                      strres[place] = (char*)malloc((strlen(buffer) + 3) * sizeof *strres[place]);
                      strres[place] = strcpy(strres[place], buffer);
                      place++;
                    }
                  }
                
                  strres[place] = (char*)malloc(sizeof *strres[place]);
                  strres[place][0] = '\0';
                
                  return strres;
                }
                
                void free_strar(char ** str_ar) {
                  for (int i = 0 ; i < size_strar(str_ar) ; i++) {
                    free(str_ar[i]);
                  }
                  free(str_ar);
                }
                
                char** get_argv()
                {
                    char* cmdline = (char*)GetCommandLineA();
                    printf("CMD LINE: %s\n", cmdline);
                
                    char** args = strsplit(cmdline, ' ');
                    return args;
                }
                """),
                ArgsComponent(code="args = get_argv();")
            ]
        elif language == Language.CSHARP:
            ArgsComponent(code=r"""
            if (args == null)
            {
                args = new Object[] { Environment.GetCommandLineArgs() };
            }else{
                args = new Object[] { args };
            }
            """)
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="EvalArgs", libraries=libraries, components=components, arch=arch)
        self.filter_string = ""
