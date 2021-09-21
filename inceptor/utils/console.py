from colorama import Fore


class Console:

    @staticmethod
    def write(what, color=Fore.WHITE):
        index = what.find("]")
        if index > -1:
            what = f"{color}{what[:index + 1]}{Fore.WHITE}{what[index + 1:]}"
        else:
            what = f"{color}{what}{Fore.WHITE}"
        print(what, end='')

    @staticmethod
    def write_line(what, color=Fore.WHITE):
        index = what.find("]")
        if index > -1:
            what = f"{color}{what[:index + 1]}{Fore.WHITE}{what[index + 1:]}{Fore.WHITE}"
        else:
            what = f"{color}{what}{Fore.WHITE}"
        print(what)

    @staticmethod
    def success(what):
        Console.write(what=what, color=Fore.LIGHTGREEN_EX)

    @staticmethod
    def success_line(what):
        Console.write_line(what=what, color=Fore.LIGHTGREEN_EX)

    @staticmethod
    def fail(what):
        Console.write(what=what, color=Fore.RED)

    @staticmethod
    def fail_line(what):
        Console.write_line(what=what, color=Fore.RED)

    @staticmethod
    def info(what):
        Console.write(what=what, color=Fore.LIGHTBLUE_EX)

    @staticmethod
    def info_line(what):
        Console.write_line(what=what, color=Fore.LIGHTBLUE_EX)

    @staticmethod
    def progress(what):
        Console.write(what=what, color=Fore.CYAN)

    @staticmethod
    def progress_line(what):
        Console.write_line(what=what, color=Fore.CYAN)

    @staticmethod
    def warn(what):
        Console.write(what=what, color=Fore.YELLOW)

    @staticmethod
    def warn_line(what):
        Console.write_line(what=what, color=Fore.YELLOW)

    @staticmethod
    def debug(what):
        Console.write(what=what, color=Fore.LIGHTYELLOW_EX)

    @staticmethod
    def debug_line(what):
        Console.write_line(what=what, color=Fore.LIGHTYELLOW_EX)

    @staticmethod
    def auto(what):
        if what.find("[+]") > -1:
            Console.success(what=what)
        elif what.find("[*]") > -1:
            Console.info(what=what)
        elif what.find("[>]") > -1:
            Console.progress(what=what)
        elif what.find("[#]") > -1 or what.find("[WARNING]") > -1 or what.find("[WARN]") > -1:
            Console.warn(what=what)
        elif what.find("[D]") > -1 or what.find("[DEBUG]") > -1:
            Console.debug(what=what)
        elif what.find("[-]") > -1:
            Console.fail(what=what)
        elif what == "Success" or what == "Done":
            Console.success(what=what)
        elif what == "Fail":
            Console.fail(what=what)
        else:
            Console.write(what=what)

    @staticmethod
    def auto_line(what):
        if what.find("[+]") > -1:
            Console.success_line(what=what)
        elif what.find("[*]") > -1:
            Console.info_line(what=what)
        elif what.find("[>]") > -1:
            Console.progress_line(what=what)
        elif what.find("[#]") > -1 or what.find("[WARNING]") > -1 or what.find("[WARN]") > -1:
            Console.warn_line(what=what)
        elif what.find("[D]") > -1 or what.find("[DEBUG]") > -1:
            Console.debug_line(what=what)
        elif what.find("[-]") > -1:
            Console.fail_line(what=what)
        elif what == "Success" or what == "Done":
            Console.write_line(what=what, color=Fore.LIGHTWHITE_EX)
        elif what == "Fail":
            Console.fail_line(what=what)
        else:
            Console.write_line(what=what)
