import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from werkzeug.utils import secure_filename

from database.db import get_connection
from ai.classifier import classify_environmental_issue


reports_bp = Blueprint(
    "reports",
    __name__
)


def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in current_app.config[
        "ALLOWED_EXTENSIONS"
    ]


@reports_bp.route("/reports/new", methods=["GET", "POST"])
def new_report():

    if "user" not in session:

        flash(
            "Please login to submit a report.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        severity = request.form.get(
            "severity",
            "Medium"
        )

        if not title or not description:

            flash(
                "Title and description are required.",
                "danger"
            )

            return redirect(
                url_for("reports.new_report")
            )

        # AI classification
        ai_result = classify_environmental_issue(
            description
        )

        category = ai_result["category"]
        priority_score = ai_result["priority_score"]

        image_filename = None

        image = request.files.get("image")

        if image and image.filename:

            if allowed_file(image.filename):

                original_name = secure_filename(
                    image.filename
                )

                extension = original_name.rsplit(
                    ".",
                    1
                )[1].lower()

                image_filename = (
                    str(uuid.uuid4())
                    + "."
                    + extension
                )

                upload_folder = current_app.config[
                    "UPLOAD_FOLDER"
                ]

                os.makedirs(
                    upload_folder,
                    exist_ok=True
                )

                image.save(
                    os.path.join(
                        upload_folder,
                        image_filename
                    )
                )

            else:

                flash(
                    "Invalid image format.",
                    "danger"
                )

                return redirect(
                    url_for("reports.new_report")
                )

        user_id = session["user"]["id"]

        conn = get_connection(current_app)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO reports
            (
                user_id,
                title,
                category,
                description,
                location,
                severity,
                priority_score,
                status,
                image
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            title,
            category,
            description,
            location,
            severity,
            priority_score,
            "Submitted",
            image_filename
        ))

        # Reward user for contributing a report
        cursor.execute("""
            UPDATE users
            SET eco_points = eco_points + 15
            WHERE id = %s
        """, (user_id,))

        conn.commit()

        cursor.close()
        conn.close()

        flash(
            "Environmental report submitted successfully. "
            "You earned 15 Eco Points!",
            "success"
        )

        return redirect(
            url_for("reports.my_reports")
        )

    return render_template(
        "report_form.html"
    )


@reports_bp.route("/reports")
def my_reports():

    if "user" not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    user_id = session["user"]["id"]

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM reports
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))

    reports = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "reports.html",
        reports=reports
    )


@reports_bp.route(
    "/reports/<int:report_id>/feedback",
    methods=["POST"]
)
def feedback(report_id):

    if "user" not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    user_id = session["user"]["id"]

    rating = request.form.get(
        "rating",
        type=int
    )

    comment = request.form.get(
        "comment",
        ""
    ).strip()

    if not rating or rating < 1 or rating > 5:

        flash(
            "Rating must be between 1 and 5.",
            "danger"
        )

        return redirect(
            url_for("reports.my_reports")
        )

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    # Check that the report belongs to the logged-in user
    cursor.execute("""
        SELECT id
        FROM reports
        WHERE id = %s
        AND user_id = %s
    """, (
        report_id,
        user_id
    ))

    report = cursor.fetchone()

    if not report:

        cursor.close()
        conn.close()

        flash(
            "Report not found.",
            "danger"
        )

        return redirect(
            url_for("reports.my_reports")
        )

    cursor.close()

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback
        (
            report_id,
            user_id,
            rating,
            comment
        )
        VALUES
        (%s, %s, %s, %s)
    """, (
        report_id,
        user_id,
        rating,
        comment
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        "Thank you for your feedback.",
        "success"
    )

    return redirect(
        url_for("reports.my_reports")
    )