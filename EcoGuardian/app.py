from flask import Flask, render_template, session
from config import Config
from database.db import init_db

# Import authentication from routes/auth.py

from routes.login import auth_bp
# Import application modules
from routes.dashboard import dashboard_bp
from routes.awareness import awareness_bp
from routes.reports import reports_bp
from routes.quiz import quiz_bp
from routes.challenges import challenges_bp
from routes.assistant import assistant_bp
from routes.admin import admin_bp


# Create Flask application
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize the database
init_db(app)


# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(awareness_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(challenges_bp)
app.register_blueprint(assistant_bp)
app.register_blueprint(admin_bp)


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Make user details available to HTML templates
@app.context_processor
def inject_user():
    user = session.get("user", {})

    return {
        "current_user": user,
        "is_admin": user.get("role") == "admin"
    }


# Handle page not found
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


# Handle internal server errors
@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


# Run the application
if __name__ == "__main__":
    app.run(debug=True)