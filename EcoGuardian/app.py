from flask import Flask, render_template, session
from config import Config
from database.db import init_db

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.awareness import awareness_bp
from routes.reports import reports_bp
from routes.quiz import quiz_bp
from routes.challenges import challenges_bp
from routes.assistant import assistant_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

init_db(app)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(awareness_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(challenges_bp)
app.register_blueprint(assistant_bp)
app.register_blueprint(admin_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.context_processor
def inject_user():
    user = session.get("user", {})

    return {
        "current_user": user,
        "is_admin": user.get("role") == "admin"
    }


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)