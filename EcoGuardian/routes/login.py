from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import get_connection

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 6:
            flash("Enter all details. Password must have 6 characters.", "danger")
            return render_template("register.html")

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, generate_password_hash(password))
            )
            conn.commit()
            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("auth.login"))

        except Exception:
            conn.rollback()
            flash("Email already exists or registration failed.", "danger")

        finally:
            cur.close()
            conn.close()

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }

            flash("Login successful!", "success")
            return redirect(url_for("dashboard.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))