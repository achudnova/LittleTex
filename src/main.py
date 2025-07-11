"""Entry point for the LittleTex application."""

from src.cli.argument_parser import ArgumentParser
from src.core.app import LittleTexApp


def run_app() -> None:
    """Entry point for the littletex command."""
    config = ArgumentParser.parse_args()
    app = LittleTexApp(config)
    app.run()


if __name__ == "__main__":
    run_app()
