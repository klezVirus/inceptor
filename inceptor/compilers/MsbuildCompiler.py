import os
import re
import subprocess
import uuid
from pathlib import Path

from compilers.Compiler import Compiler
from compilers.CompilerExceptions import OperationNotSupported
from config.Config import Config
from engine.enums.Enums import LinkingMode
import lxml.etree

from utils.utils import get_temporary_file, get_project_root, assembly_name


class MsbuildCompiler(Compiler):

    def add_include_directory(self, directory):
        pass

    def set_linking_mode(self, linking_mode):
        self.linking_mode = linking_mode

    def __init__(self, args=None, aargs=None, arch="x64"):
        self.config = Config()
        super().__init__(None, args=args, aargs=aargs, sep=":", arch=arch)
        if not self.args:
            self.args = {}
        self.linking_mode = LinkingMode.LIBRARY
        self.csproj_data = ""
        self.target = "EXE"
        self.outfile = None
        self.libraries = []
        self.icon = None

    def default_exe_args(self, outfile):
        self.target = "EXE"
        self.outfile = outfile

    def default_dll_args(self, outfile):
        self.target = "Library"
        self.outfile = outfile

    def hide_window(self):
        if self.target.lower() == "exe":
            self.target = "WinExe"
        else:
            raise OperationNotSupported(
                "DLLs don't support hidden windows at compiler level. Consider using SW_HIDE in the template"
            )
        return True

    def set_outfile(self, outfile):
        self.outfile = f'"{outfile}"'

    def set_architecture(self, arch):
        self.arch = arch

    def set_libraries(self, libs: list):
        if len(libs) > 0:
            for lib in libs:
                self.libraries.append(lib)

    def set_icon(self, icon: Path):
        self.icon = f'"{str(icon.absolute())}"'

    def get_csproj(self):
        return rf"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Import Project="$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props" Condition="Exists('$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props')" />
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Release</Configuration>
    <Platform Condition=" '$(Platform)' == '' ">{self.arch}</Platform>
    <ProjectGuid>{{{uuid.uuid4()}}}</ProjectGuid>
    <OutputType>{self.target}</OutputType>
    <RootNamespace>Inceptor</RootNamespace>
    <AssemblyName>{os.path.basename(os.path.splitext(self.outfile)[0])}</AssemblyName>
    <TargetFrameworkVersion>v4.7.2</TargetFrameworkVersion>
    <FileAlignment>512</FileAlignment>
    <AutoGenerateBindingRedirects>true</AutoGenerateBindingRedirects>
    <Deterministic>true</Deterministic>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug|AnyCPU' ">
    <PlatformTarget>AnyCPU</PlatformTarget>
    <DebugSymbols>true</DebugSymbols>
    <DebugType>full</DebugType>
    <Optimize>false</Optimize>
    <OutputPath>.\</OutputPath>
    <DefineConstants>DEBUG;TRACE</DefineConstants>
    <ErrorReport>prompt</ErrorReport>
    <WarningLevel>4</WarningLevel>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Release|AnyCPU' ">
    <PlatformTarget>AnyCPU</PlatformTarget>
    <DebugType>pdbonly</DebugType>
    <Optimize>true</Optimize>
    <OutputPath>.\</OutputPath>
    <DefineConstants>TRACE</DefineConstants>
    <ErrorReport>prompt</ErrorReport>
    <WarningLevel>4</WarningLevel>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)' == 'Debug|x64'">
    <DebugSymbols>true</DebugSymbols>
    <OutputPath>.\</OutputPath>
    <DefineConstants>DEBUG;TRACE</DefineConstants>
    <DebugType>full</DebugType>
    <PlatformTarget>x64</PlatformTarget>
    <LangVersion>7.3</LangVersion>
    <ErrorReport>prompt</ErrorReport>
    <Prefer32Bit>true</Prefer32Bit>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)' == 'Release|x64'">
    <OutputPath>.\</OutputPath>
    <DefineConstants>TRACE</DefineConstants>
    <Optimize>true</Optimize>
    <DebugType>pdbonly</DebugType>
    <PlatformTarget>x64</PlatformTarget>
    <LangVersion>7.3</LangVersion>
    <ErrorReport>prompt</ErrorReport>
    <Prefer32Bit>true</Prefer32Bit>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="System" />
    <Reference Include="System.Core" />
    <Reference Include="System.Xml.Linq" />
    <Reference Include="System.Data.DataSetExtensions" />
    <Reference Include="Microsoft.CSharp" />
    <Reference Include="System.Data" />
    <Reference Include="System.Net.Http" />
    <Reference Include="System.Xml" />
    <!-- ####LIBRARIES#### -->
  </ItemGroup>
  <ItemGroup>
    <!-- ####INPUT#### -->
  </ItemGroup>
    <ItemGroup>
    <BootstrapperPackage Include=".NETFramework,Version=v4.7.2">
      <Visible>False</Visible>
      <ProductName>Microsoft .NET Framework 4.7.2 %28x86 and x64%29</ProductName>
      <Install>true</Install>
    </BootstrapperPackage>
    <BootstrapperPackage Include="Microsoft.Net.Framework.3.5.SP1">
      <Visible>False</Visible>
      <ProductName>.NET Framework 3.5 SP1</ProductName>
      <Install>false</Install>
    </BootstrapperPackage>
  </ItemGroup>

  <Import Project="$(MSBuildToolsPath)\Microsoft.CSharp.targets" />
</Project>
        """

    def compile(self, files: list):
        file_arg = get_temporary_file(".csproj")
        self.csproj_data = self.get_csproj()
        for file in files:
            if not os.path.isfile(file):
                print(f"[-] Compiler: File {file} not found")
            else:
                self.csproj_data = self.csproj_data.replace(
                    "<!-- ####INPUT#### -->",
                    f'<Compile Include="{file}" />\n<!-- ####INPUT#### -->'
                )
        for lib in self.libraries:
            self.csproj_data = self.csproj_data.replace(
                "<!-- ####LIBRARIES#### -->",
                rf"""
    <Reference Include="{assembly_name(lib)}, processorArchitecture=MSIL">
      <HintPath>{Path(lib).relative_to(get_project_root())}</HintPath>
      <Private>True</Private>
      <Private>True</Private>
    </Reference>
<!-- ####LIBRARIES#### -->
                """
            )
        self.csproj_data = re.sub(r"<!--[\s|\w|\#]*-->", "", self.csproj_data)
        with open(file_arg, "w") as csproj:
            csproj.write(self.csproj_data)
        try:
            cmd = f"\"{self.path}\" {file_arg}"
            if self.prefix_cmd:
                cmd = f"{self.prefix_cmd} & {cmd}"
            if self.suffix_cmd:
                cmd = f"{cmd} & {self.suffix_cmd}"
            if Config().get_boolean("DEBUG", "COMPILERS"):
                print(cmd)
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if Config().get_boolean("DEBUG", "COMPILERS"):
                print(output.decode())
        except subprocess.CalledProcessError as e:
            for line in e.output.decode().split("\n"):
                if re.search(r"error", line, re.IGNORECASE):
                    print(f"  [-] Error: {line}")
                if re.search(r"warnin", line, re.IGNORECASE):
                    print(f"  [-] Warning: {line}")
            raise Exception("Compiler Error")
        return True