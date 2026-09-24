from flask import Blueprint, render_template, session, redirect, url_for, flash
from database.db import get_connection
from flask import current_app


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():

    if "user" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user"]["id"]

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    # Get user details
    cursor.execute("""
        SELECT id, name, email, role, eco_points
        FROM users
        WHERE id = %s
    """, (user_id,))

    user = cursor.fetchone()

    # Number of reports
    cursor.execute("""
        SELECT COUNT(*) AS total_reports
        FROM reports
        WHERE user_id = %s
    """, (user_id,))

    report_data = cursor.fetchone()

    # Number of quiz attempts
    cursor.execute("""
        SELECT COUNT(*) AS quiz_attempts
        FROM quiz_results
        WHERE user_id = %s
    """, (user_id,))

    quiz_data = cursor.fetchone()

    # Recent reports
    cursor.execute("""
        SELECT
            id,
            title,
            category,
            severity,
            status,
            priority_score,
            created_at
        FROM reports
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,))

    recent_reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        user=user,
        total_reports=report_data["total_reports"],
        quiz_attempts=quiz_data["quiz_attempts"],
        recent_reports=recent_reports
    )