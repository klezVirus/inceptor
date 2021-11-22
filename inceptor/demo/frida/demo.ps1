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
        $FilePath
    )

    if (-not (Test-Path -Path $FilePath)) {
        Write-Error "$FilePath does not exist"
        return
    }


    $FileFullPath = Resolve-Path -Path $FilePath

    # Step 1: Spawn sacrificial process
    # This process will be used to perform the shellcode injection

    Write-Host "[*] Starting Notepad"
    $pHandle = (Start-Process "notepad.exe" -PassThru)
    Sleep 1
    $victim_pid = $pHandle.Id

    # Step 2: Start the implant
    # If everyting works fine, the implant should wait 5-15 seconds to execute the code
    # NW: Ensure you've packed the shellcode using the --delay option!!!

    Write-Host "[*] Starting code injection demo loader"
    $demoHandle = (Start-Process "$FileFullPath" -PassThru -Args $victim_pid)
    Sleep 1
    $demo_pid = $demoHandle.Id

    # If you'd like to see the difference between Native and .NET when using Syscalls,
    # add also the hooks for NtAllocateVirtualMemory and NtWriteVirtualMemory
    # $hooked_array = @("NtCreateThreadEx", "NtAllocateVirtualMemory", "NtWriteVirtualMemory")
    $hooked_array = @("NtCreateThreadEx")
    $hooked = [string]::join(" -i ", $hooked_array)

    # Step 3: Start frida-trace against the implant, trying to intercept native APIs
    # Target APIs are "NtCreateThreadEx", "NtAllocateVirtualMemory", "NtWriteVirtualMemory"

    Write-Host "[*] Starting frida hooking"
    Write-Host "[*] Intercepting $hooked_array"
    Start-Process "cmd.exe" -Args "/k frida-trace -x ntdll.dll -i $hooked -p $demo_pid"

}

Invoke-Demo -FilePath "$args"