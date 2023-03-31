# pylint: disable=no-value-for-parameter
import click
from werkzeug.security import generate_password_hash

from crms.app import app
from crms.models import User


@click.command()
@click.option("--name", required=True, prompt="Username", help="Name of the user")
@click.option("--email", required=True, prompt="Email", help="Email of the user")
@click.option(
    "--password", required=True, prompt="Password", help="The most secret password."
)
def add_user(name: str, email: str, password: str) -> None:
    with app.app_context():
        User.create(
            name=name,
            email=email,
            password=generate_password_hash(password, method="sha256"),
            commit=True,
        )


if __name__ == "__main__":
    add_user()
