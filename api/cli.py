import typer
import uvicorn
from sqlmodel import Session

from .config import settings
from .db import engine
from .models import User

cli = typer.Typer(name="API")


@cli.command()
def run(
    port: int = settings.server.port,
    host: str = settings.server.host,
    log_level: str = settings.server.log_level,
    reload: bool = settings.server.reload,
):  # pragma: no cover
    """Run the API server."""
    uvicorn.run(
        "api.app:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )


@cli.command()
def create_user(
    email: str, username: str, password: str, is_admin: bool = False
):
    """Create user"""
    with Session(engine) as session:
        user = User(
            email=email,
            username=username,
            password=password,
            is_admin=is_admin,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        typer.echo(f"created {username} user")
        return user
