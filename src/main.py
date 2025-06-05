from src.cli import main_cli

def run_app() -> None:
    """Wrapper function to run the LittleTex application."""
    print("Starting LittleTex application...")
    main_cli()
    print("LittleTex application finished.")

if __name__ == "__main__":
    run_app()