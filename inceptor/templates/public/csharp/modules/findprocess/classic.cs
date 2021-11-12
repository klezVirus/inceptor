using System.Diagnostics;

namespace ####NAMESPACE####
{

    public static class ####CLASS####
    {

        public static int ####FUNCTION####() {
            int pid = -1;
            string[] processes = new string[]{
                ####PROCESS####
            };
            foreach (string process in processes){
                pid = FindProcess(process);
                if (pid == -1){
                    break;
                }
            }
            if (pid == -1){
                pid = Process.GetCurrentProcess().Id;
            }
            return pid;
        }

        public static int FindProcess(string processName) {
            int pid = -1;
            Process[] processes = Process.GetProcessesByName(processName);
            if (processes.Length > 0) {
                pid = processes[0].Id;
            }
            return pid;
        }
    }
}
