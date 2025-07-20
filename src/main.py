"""Entry point for the LittleTex application."""

import sys
from src.cli.splash import show_splash_screen
from src.cli.argument_parser import ArgumentParser
from src.core.app import LittleTexApp


def run_app() -> None:
    """Entry point for the littletex command."""
    if len(sys.argv) == 1:
        show_splash_screen()
        return

    config = ArgumentParser.parse_args()
    app = LittleTexApp(config)
    app.run()


if __name__ == "__main__":
    run_app()
