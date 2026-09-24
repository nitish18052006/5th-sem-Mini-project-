from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from database.db import get_connection


challenges_bp = Blueprint(
    "challenges",
    __name__
)


@challenges_bp.route("/challenges")
def challenges():

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
        SELECT
            c.*,
            CASE
                WHEN cp.id IS NULL THEN 0
                ELSE 1
            END AS completed
        FROM challenges c
        LEFT JOIN challenge_progress cp
            ON c.id = cp.challenge_id
            AND cp.user_id = %s
        ORDER BY c.id
    """, (user_id,))

    challenges_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "challenges.html",
        challenges=challenges_data
    )


@challenges_bp.route(
    "/challenges/<int:challenge_id>/complete"
)
def complete_challenge(challenge_id):

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
        FROM challenges
        WHERE id = %s
    """, (challenge_id,))

    challenge = cursor.fetchone()

    if not challenge:

        cursor.close()
        conn.close()

        flash(
            "Challenge not found.",
            "danger"
        )

        return redirect(
            url_for("challenges.challenges")
        )

    cursor.execute("""
        SELECT id
        FROM challenge_progress
        WHERE user_id = %s
        AND challenge_id = %s
    """, (
        user_id,
        challenge_id
    ))

    already_completed = cursor.fetchone()

    if already_completed:

        cursor.close()
        conn.close()

        flash(
            "You have already completed this challenge.",
            "info"
        )

        return redirect(
            url_for("challenges.challenges")
        )

    cursor.execute("""
        INSERT INTO challenge_progress
        (
            user_id,
            challenge_id
        )
        VALUES
        (%s, %s)
    """, (
        user_id,
        challenge_id
    ))

    cursor.execute("""
        UPDATE users
        SET eco_points = eco_points + %s
        WHERE id = %s
    """, (
        challenge["points"],
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    flash(
        f"Challenge completed! "
        f"You earned {challenge['points']} Eco Points.",
        "success"
    )

    return redirect(
        url_for("challenges.challenges")
    )


@challenges_bp.route("/leaderboard")
def leaderboard():

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            name,
            eco_points,
            RANK() OVER (
                ORDER BY eco_points DESC
            ) AS ranking
        FROM users
        WHERE role = 'user'
        ORDER BY eco_points DESC
        LIMIT 20
    """)

    leaderboard_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard_data
    )