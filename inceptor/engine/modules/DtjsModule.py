import os
import tempfile
import uuid

from config.Config import Config
from engine.component.BypassComponent import BypassComponent
from engine.component.UsingComponent import UsingComponent
from engine.modules.AdditionalSourceModule import AdditionalSourceModule
from engine.modules.AssemblyInfoModule import AssemblyInfoModule
from engine.modules.TemplateModule import TemplateModule, ModuleNotCompatibleException
from enums.Architectures import Arch
from enums.Language import Language
from utils.utils import get_project_root


class DtjsModule(AssemblyInfoModule):
    def __init__(self):
        content = ""
        path = tempfile.NamedTemporaryFile(
            delete=False,
            dir=str(Config().get_path("DIRECTORIES", "WRITER"))
        ).name
        trademark = ""
        company = "Namco"
        title = "StreetFighter"
        description = "StreetFighter Alpha 2022 Game Preview"
        product = "StreetFighter Alpha 2022 Game Preview"
        copyright = "CapCom"
        super().__init__(
            path=path,
            title=title,
            description=description,
            company=company,
            product=product,
            copyright=copyright,
            trademark=trademark,
            assembly_version="1.0.0.0",
            file_version="1.0.0.0",
            guid=None,
            neutral_language="",
            com_visible=False,
            language=Language.CSHARP,
            arch=Arch.x64
        )
