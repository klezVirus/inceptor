using System;
using System.Drawing;
using System.IO;
using System.Reflection;

namespace ####NAMESPACE####
{
    public static class ####CLASS####{

        public static byte[] ####FUNCTION####()
        {

            var icon = Icon.ExtractAssociatedIcon(Assembly.GetExecutingAssembly().Location);
            using (MemoryStream ms = new MemoryStream())
            {
                icon.Save(ms);
                return ms.ToArray();
            }
        }
    }
}



