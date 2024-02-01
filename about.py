from colorama import Fore, Style

script_header = f'{Fore.LIGHTGREEN_EX}============================================================' \
    f'\n\n' \
    f'{Fore.LIGHTMAGENTA_EX}                      HandshakeReports{Fore.LIGHTWHITE_EX}' \
    f'{Fore.LIGHTBLACK_EX}' \
    f'\n  {Fore.LIGHTWHITE_EX}     (https://github.com/CLDC-OU/HandshakeReports)' \
    f'\n  {Fore.LIGHTBLACK_EX}                  Author: {Fore.LIGHTWHITE_EX}Claire Childers' \
    f'\n  {Fore.LIGHTBLACK_EX}                       License: {Fore.LIGHTWHITE_EX}MIT' \
    f'\n  {Fore.LIGHTBLACK_EX}                      Version: {Fore.LIGHTWHITE_EX}0.2.1' \
    f'\n\n{Fore.LIGHTBLACK_EX}' \
    f'HandshakeReports is a script that combines data collected\n' \
    f'through Handshake (https://joinhandshake.com) to generate\n' \
    f'a variable number of reports that give insight on\n' \
    f'performance of Career Services staff members, students\n' \
    f'that need a followup appointment, and referral data.\n\n' \
    f'Read the README.md file for more information.\n\n' \
    f'{Fore.LIGHTGREEN_EX}' \
    f'============================================================' \
    f'{Style.RESET_ALL}' \

print(script_header)
