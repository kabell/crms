from typing import Any

import flask_login
import structlog
from flask import Flask, Response, request
from flask_login import login_required
from flask_migrate import Migrate

from crms import config, views
from crms.login_manager import login_manager
from crms.models import db

logger = structlog.getLogger()

migrate = Migrate(compare_type=True)


def create_app(*_: Any, **kwargs: Any) -> Flask:
    """Create an application with all required setup."""

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.secret_key = config.SECRET_KEY.encode()
    app.config.update(**kwargs)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(views.app)

    @app.after_request
    def log_request_info(response: Response) -> Response:
        if request.path != "/ping":
            logger.info(
                "crms.request",
                path=request.path,
                status_code=response.status_code,
                user_agent=request.headers.get("user-agent"),
            )
        return response

    @app.route("/ping", methods=["GET"])
    @login_required
    def ping() -> dict:
        return {"ping": "pong", "username": flask_login.current_user.id}

    return app
