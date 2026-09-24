from functools import wraps

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash,
    request,
    current_app
)

from database.db import get_connection


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        if session["user"].get("role") != "admin":

            flash(
                "Admin access required.",
                "danger"
            )

            return redirect(
                url_for("dashboard.dashboard")
            )

        return function(*args, **kwargs)

    return wrapper


@admin_bp.route("/")
@admin_required
def admin_dashboard():

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    # Total users
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM users
        WHERE role = 'user'
    """)

    total_users = cursor.fetchone()["total"]

    # Total reports
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
    """)

    total_reports = cursor.fetchone()["total"]

    # Pending reports
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
        WHERE status = 'Submitted'
    """)

    pending_reports = cursor.fetchone()["total"]

    # Resolved reports
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM reports
        WHERE status = 'Resolved'
    """)

    resolved_reports = cursor.fetchone()["total"]

    # Quiz attempts
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM quiz_results
    """)

    quiz_attempts = cursor.fetchone()["total"]

    # Reports by category
    cursor.execute("""
        SELECT
            category,
            COUNT(*) AS total
        FROM reports
        GROUP BY category
        ORDER BY total DESC
    """)

    category_data = cursor.fetchall()

    # Reports by status
    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS total
        FROM reports
        GROUP BY status
    """)

    status_data = cursor.fetchall()

    # Recent reports
    cursor.execute("""
        SELECT
            r.id,
            r.title,
            r.category,
            r.severity,
            r.priority_score,
            r.status,
            r.location,
            r.created_at,
            u.name AS user_name
        FROM reports r
        JOIN users u
            ON r.user_id = u.id
        ORDER BY r.created_at DESC
        LIMIT 10
    """)

    recent_reports = cursor.fetchall()

    # Community Eco Index
    cursor.execute("""
        SELECT COALESCE(SUM(eco_points), 0) AS total_points
        FROM users
        WHERE role = 'user'
    """)

    total_points = cursor.fetchone()["total_points"]

    # Simple index calculation for dashboard display
    if total_users > 0:
        eco_index = round(
            total_points / total_users
        )
    else:
        eco_index = 0

    cursor.close()
    conn.close()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_reports=total_reports,
        pending_reports=pending_reports,
        resolved_reports=resolved_reports,
        quiz_attempts=quiz_attempts,
        category_data=category_data,
        status_data=status_data,
        recent_reports=recent_reports,
        eco_index=eco_index
    )


@admin_bp.route(
    "/report/<int:report_id>/status",
    methods=["POST"]
)
@admin_required
def update_report_status(report_id):

    status = request.form.get(
        "status",
        "Submitted"
    )

    allowed_statuses = {
        "Submitted",
        "Under Review",
        "In Progress",
        "Resolved",
        "Rejected"
    }

    if status not in allowed_statuses:

        flash(
            "Invalid status.",
            "danger"
        )

        return redirect(
            url_for("admin.admin_dashboard")
        )

    conn = get_connection(current_app)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reports
        SET status = %s
        WHERE id = %s
    """, (
        status,
        report_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Report status updated successfully.",
        "success"
    )

    return redirect(
        url_for("admin.admin_dashboard")
    )