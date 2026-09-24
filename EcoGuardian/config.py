import os


class Config:

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "ecoguardian-secret-key"
    )

    MYSQL_HOST = os.environ.get(
        "MYSQL_HOST",
        "localhost"
    )

    MYSQL_PORT = int(
        os.environ.get(
            "MYSQL_PORT",
            "3306"
        )
    )

    MYSQL_USER = os.environ.get(
        "MYSQL_USER",
        "root"
    )

    MYSQL_PASSWORD = os.environ.get(
        "MYSQL_PASSWORD",
        "system"
    )

    MYSQL_DATABASE = os.environ.get(
        "MYSQL_DATABASE",
        "ecoguardian"
    )

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "static",
        "uploads"
    )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp"
    }