:triangular_flag_on_post: This is the public repository of CrackMapExec, for latest version and updates please consider supporting us through https://porchetta.industries/

<h1 align="center">
<br>
<img src=./images/inceptor-logo.png >
<br>
</h1>

## :triangular_flag_on_post: Sponsors

If you want to sponsors this project and have the latest updates on CME, latest issues fixed, latest features, please support us on https://porchetta.industries/

## Official Discord Channel

Come hang out on Discord!

[![Porchetta Industries](https://discordapp.com/api/guilds/736724457258745996/widget.png?style=banner3)](https://discord.gg/ycGXUxy)

# Table of content

* [Overview](#overview)
* [Installation](#installation)
* [Usage](#usage)

## News

NW: We're currently working to improve the template engine! As soon as we release the next version, instructions on how 
to use, customize, and extend the tool, will be available in the [Wiki][13]. 

## Overview

Modern Penetration testing and Red Teaming often requires to bypass common AV/EDR appliances in order to execute code 
on a target. With time, defenses are becoming more complex and inherently more difficult to bypass consistently. 

Inceptor is a tool which can help to automate great part of this process, hopefully requiring no further effort.

## Features

Inceptor is a template-based PE packer for Windows, designed to help penetration testers and red teamers to bypass
common AV and EDR solutions. Inceptor has been designed with a focus on usability, and to allow extensive user 
customisation.

To have a good overview of what it was implemented and why, it might be useful to tak a look to the following resources:

* [The path to code execution in the era of EDR, Next-Gen AVs, and AMSI](https://klezvirus.github.io/RedTeaming/AV_Evasion/CodeExeNewDotNet/)
* [Inceptor - Bypass AV-EDR solutions combining well known techniques](https://github.com/klezVirus/inceptor/blob/main/slides/Inceptor%20-%20Bypass%20AV-EDR%20solutions%20combining%20well%20known%20techniques.pdf)

### Shellcode Transformation/Loading

Inceptor is able to convert existing EXE/DLL into shellcode using various open-source converters:

* [Donut](https://github.com/TheWover/donut): Donut is "The Converter". This tool is more like a piece of art by [TheWover][3], 
  and can be used to transform Native binaries, DLL, and .Net binaries into position independent code shellcode.
* [sRDI](https://github.com/monoxgas/sRDI): By [Monoxgas][4], this tool can convert existing naticcve DLL into PIC, which can then be injected as regular shellcode. 
* [Pe2Sh](https://github.com/hasherezade/pe_to_shellcode): By [Hasherazade][5], this tool can convert an existing native 
  EXE into PIC shellcode, which can also be run as a normal EXE.

### LI Encoders vs LD Encoders

Inceptor can encode, compress, or encrypt shellcode using different means. While developing the tool, I started differentiating 
between what I call loader-independent (LI) encoding, and loader-dependent (LD) encoding.

Loader-independent encoding is a type of encoding not managed by the template chosen by the user (loader). This usually 
means that the decoding stub is not part of the template, but embedded in the shellcode itself. 
Inceptor offers this kind of feature using the open-source tool [sgn](https://github.com/EgeBalci/sgn), which is used to 
make the payload polymorphic and undetectable using common signature detection.

Even strong at it is, Shikata-Ga-Nai is not really suitable for certain templates. For this reason, 
Inceptor also implements Loader-dependent encoders, which are designed to let the loader taking care of 
the decoding. As such, LD encoders install the decoding stub directly in the template. 
This kind of encoders, as implemented within Inceptor, are also "Chainable", meaning they can be chained together to
encode a payload. 

While using a chain of encoders can sometimes improve the obfuscation of a given payload, 
this technique can also expose multiple decoding routines, which can help Defenders to design 
signatures against them. For this reason, Inceptor offers multiple ways to obfuscate the final
artifacts, hardening the RE process.

At the time of writing, the public version of Inceptor has been provided with the following encoders/compressors/encryptors:

- Native
  * Xor
  * Nop (Insertion)
- .NET
  * Hex
  * Base64
  * Xor
  * Nop (Insertion)
  * AES
  * Zlib
  * RLE
- PowerShell
  * Hex
  * Base64
  * Xor
  * Nop (Insertion)
  * AES
  
Inceptor can validate an encoding chain both statically and dynamically, statically checking the decoders' 
input/output types, and also dynamically verifying the implementation with an independent implementation. 

At any time, a user can easily validate a chain using the `chain-validate.py` utility.

### AV Evasion Mechanisms

Inceptor also natively implements AV Evasion mechanisms, and as such, it offers the possibility to include AV evasion 
features to the payload in the form of "modules" (plugins). 

The plugins which can be embedded are:

* [x] AMSI bypass
* [x] WLDP bypass
* [x] ETW bypass
* [x] Sandbox (Behavioural) Deception

### EDR Evasion Mechanisms

Inceptor also implements EDR Evasion mechanisms, such as full unhooking, direct syscall invocation and manual DLL mapping.
Direct Syscalls are implemented in C# using the outstanding "[DInvoke][9]" project, 
again by [TheWover][1].
In C/C++, Syscalls are implemented using [SysWhispers][7] and [SysWhispers2][8] projects, by [Jackson_T][6]. In addition, 
Inceptor has built-in support for x86 Syscalls as well.

As the AV bypass features, these features can be enabled as modules, with the only difference that they require 
operating on a template which supports them. The techniques implemented so far are:

* [x] Full Unhooking
* [x] Manual DLL Mapping
* [x] Direct Syscalls 

### Obfuscation

Inceptor supports payload obfuscation by using external utils, such as [ConfuserEx](https://github.com/mkaring/ConfuserEx) 
and [Chameleon](https://github.com/klezVirus/chameleon), and provides support for C/C++ obfuscation using [LLVM-Obfuscator](https://github.com/klezVirus/obfuscator), which
is an IR-based obfuscator using the LLVM compilation platform.

- [x] PowerShell
- [x] C#
- [x] C/C++

### Code Signing

Another feature of Inceptor is that it can code sign the resulting binary/dll by using the tool [CarbonCopy][10]
Usually, files signed with code signing certificates are less strictly analysed. Many anti-malware products 
don't validate/verify these certificates.

### Workflow

The full workflow can be summarized in the following high-level, and simplified scheme:

![Workflow](./images/workflow.png)

<!-- install -->
## Installation

Inceptor has been designed to work on Windows. The `update-config.py` utility can locate the required Microsoft binaries
and update the configuration accordingly. It might be required to install Microsoft Build Tools, the Windows SDK,
and Visual Studio, `update-config.py` will guide the user on how to install the required dependencies.

```
git clone --recursive https://github.com/klezVirus/inceptor.git
cd inceptor
virtualenv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
cd inceptor
python update-config.py
```
<!-- installstop -->

## Useful Notes

#### Default Loaders

The current version of Inceptor locates a specific template using a simple naming convention (don't change template names),
and the set of arguments given by the user. Among the arguments, there is also the loader (-t). If not specified, the loader
will be picked-up as a function of the file to pack, following this simple schema:

```
$ python inceptor.py -hh

[*] Default Loaders
      Input File Extension SpecialCondition   Guessed Filetype Default Loader  Default Template
0                     .raw              NaN          Shellcode  Simple Loader           Classic
1                     .exe             .NET  Dotnet Executable          Donut           Classic
2                     .exe              NaN  Native Executable   Pe2Shellcode           PE Load
3                     .dll              NaN     Native Library           sRDI           Classic
```

#### Template name convention

It's very important to understand also the template name convention, to avoid misinterpreting an artifact behaviour.

* Classic: a classic template usually means it uses the VirtualAlloc/VirtualAllocEx and CreateThread/CreateRemoteThread 
  API to allocate and execute arbitrary code
* Dinvoke: if a template contains only dinvoke (e.g classic-dinvoke.cs), it means it uses dynamic function resolution
  feature of dinvoke
* dinvoke-_subtechnique_: a template containing dinvoke followed by another keyword is using a particular feature of
  dinvoke, like manual_mapping, overload_mapping, or syscalls
* Syscalls: as the name suggest, this template is using syscalls
* PE Load: this template tries to map a full PE into memory, without transforming it
* Assembly Load: this template tries to execute a .NET assembly using reflection

<!-- usage -->
## Usage
```
$ usage: inceptor.py [-h] [-hh] [-Z] {native,dotnet,powershell} ...

inceptor: A Windows-based PE Packing framework designed to help 
          Red Team Operators to bypass common AV and EDR solutions

positional arguments:
  {native,dotnet,powershell}
    native              Native Binaries Generator
    dotnet              .NET Binaries Generator
    powershell          PowerShell Wrapper Scripts Generator

optional arguments:
  -h, --help            show this help message and exit
  -hh                   Show functional table
  -Z, --check           Check file against ThreatCheck
```

<!-- usagestop -->

## Next Developments

* New Template Engine
* New Templates
* New Encoders
* C# Code-Based obfuscation

## Resources

* [Inceptor - Bypass AV-EDR solutions combining well known techniques](https://github.com/klezVirus/inceptor/blob/main/slides/Inceptor%20-%20Bypass%20AV-EDR%20solutions%20combining%20well%20known%20techniques.pdf)
* [A tale of EDR bypass methods](https://s3cur3th1ssh1t.github.io/A-tale-of-EDR-bypass-methods)

[1]: https://github.com/phra/PEzor
[2]: https://github.com/forrest-orr/artifacts-kit
[3]: https://twitter.com/TheRealWover
[4]: https://twitter.com/monoxgas
[5]: https://twitter.com/hasherezade
[6]: https://twitter.com/Jackson_T
[7]: https://github.com/jthuraisamy/SysWhispers
[8]: https://github.com/jthuraisamy/SysWhispers2
[9]: https://github.com/TheWover/DInvoke
[10]: https://github.com/paranoidninja/CarbonCopy
[11]: https://twitter.com/phraaaaaaa
[12]: https://twitter.com/_ForrestOrr
[13]: https://github.com/klezVirus/inceptor/wiki