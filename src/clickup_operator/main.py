import asyncio
from .server import main

def run():
    """Entry point for the CLI."""
    asyncio.run(main())
    
def cli():
    """Entrypoint for console script."""
    run()

if __name__ == "__main__":
    cli()