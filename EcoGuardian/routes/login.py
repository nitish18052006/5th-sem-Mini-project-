
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, current_app
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from database.db import get_connection

# Create authentication blueprint
auth_bp = Blueprint("auth", __name__)


# User Registration
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "danger")
            return redirect(url_for("auth.register"))

        conn = get_connection(current_app)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            if cursor.fetchone():
                flash("Email is already registered.", "warning")
                return redirect(url_for("auth.register"))

            hashed_password = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO users
                (name, email, password, role, eco_points)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, email, hashed_password, "user", 0))

            conn.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")


# User Login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        conn = get_connection(current_app)
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user"] = {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }

            flash("Login successful!", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin.admin_dashboard"))

            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# User Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
