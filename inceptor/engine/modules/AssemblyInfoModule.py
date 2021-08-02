import os
import uuid

from engine.component.BypassComponent import BypassComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.AdditionalSourceModule import AdditionalSourceModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root


class AssemblyInfoModule(AdditionalSourceModule):
    def __init__(self,
                 path,
                 title,
                 description="",
                 company="",
                 product="",
                 copyright="",
                 trademark="",
                 assembly_version="1.0.0.0",
                 file_version="1.0.0.0",
                 guid=None,
                 neutral_language="",
                 com_visible=False,
                 language=Language.CSHARP,
                 arch=Arch.x64):
        content = ""
        if not guid:
            guid = str(uuid.uuid4())
        if language == Language.CSHARP:
            content = rf"""
            using System.Resources;
            using System.Reflection;
            using System.Runtime.InteropServices;
                        
            [assembly: AssemblyTitle("{title}")]
            [assembly: AssemblyDescription("{description}")]
            [assembly: AssemblyConfiguration("")]
            [assembly: AssemblyCompany("{company}")]
            [assembly: AssemblyProduct("{product}")]
            [assembly: AssemblyCopyright("{copyright}")]
            [assembly: AssemblyTrademark("{trademark}")]
            [assembly: AssemblyCulture("")]
            [assembly: NeutralResourcesLanguage("{neutral_language}")]
            [assembly: ComVisible({'true' if com_visible else 'false'})]
            [assembly: Guid("{guid}")]
            [assembly: AssemblyVersion("{assembly_version}")]
            [assembly: AssemblyFileVersion("{file_version}")]
            """
        else:
            raise ModuleNotCompatibleException()
        super().__init__(name="AssemblyInfoModule", path=path, content=content, arch=arch)
