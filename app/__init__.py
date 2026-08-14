from pathlib import Path

from flask import Flask
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .config import Config
from .extensions import db, migrate


@event.listens_for(Engine, "connect")
def sqlite_settings(connection, _):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config: app.config.update(config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app); migrate.init_app(app, db)
    from .routes import bp
    app.register_blueprint(bp)
    return app
