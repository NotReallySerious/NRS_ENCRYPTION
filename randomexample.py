import colorama
from colorama import Fore, Style, init
import pyfiglet
import os
import time

def typewriter(text, font="cosmic", delay=0.3, color=Fore.CYAN):
    current = ""
    for char in text:
        current += char
        os.system('cls' if os.name == 'nt' else 'clear')
        print(color + pyfiglet.figlet_format(current, font=font, width=900))
        time.sleep(delay)

typewriter("N R S  E N C R Y P T I O N")
