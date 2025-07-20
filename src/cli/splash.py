"""Generate ASCII art splash screen for the CLI."""

from pyfiglet import figlet_format
from colorama import Fore, init


def show_splash_screen():
    init(autoreset=True)
    title = figlet_format("LittleTex", font="slant")
    description = "A simple, fast, and elegant Markdown to LaTeX converter."
    features = """
    === Features ===
    - Converts basic Markdown syntax (headings, lists, bold, etc.)
    - Supports PDF generation directly from the command line
    - Customizable page margins via metadata
    """
    yellow = Fore.YELLOW
    blue = Fore.BLUE
    lightred = Fore.RED
    
    print(yellow + title)
    print(yellow + description)
    print(blue + features)
    print(lightred + "For more details, run: littletex -h")
