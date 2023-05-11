""" Written by Benjamin Jack Cullen """

import colorama

# bold
# print('\033[1mfoobar\033[0m')

colorama.init()


def color(s: str, c: str) -> str:
    """ color print """
    if c == 'W':
        return str(colorama.Style.BRIGHT + colorama.Fore.WHITE + str(s) + colorama.Style.RESET_ALL)
    elif c == 'LM':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'M':
        return colorama.Style.BRIGHT + colorama.Fore.MAGENTA + str(s) + colorama.Style.RESET_ALL
    elif c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'C':
        return colorama.Style.BRIGHT + colorama.Fore.CYAN + str(s) + colorama.Style.RESET_ALL
    elif c == 'B':
        return str(colorama.Style.BRIGHT + colorama.Fore.BLUE + str(s) + colorama.Style.RESET_ALL)
    elif c == 'LG':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL
    elif c == 'BL':
        return str(colorama.Style.BRIGHT + colorama.Fore.BLACK + str(s) + colorama.Style.RESET_ALL)
