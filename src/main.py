import click
import uvicorn

from api.server import app
from config.settings import get_settings


@click.command()
@click.option("--host", default=None)
@click.option("--port", default=None, type=int)
def run(host: str | None, port: int | None) -> None:
    settings = get_settings()
    uvicorn.run(app, host=host or settings.app_host, port=port or settings.app_port)


if __name__ == "__main__":
    run()
