import random

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

from database.db import get_connection


quiz_bp = Blueprint(
    "quiz",
    __name__
)


@quiz_bp.route("/quiz")
def quiz():

    if "user" not in session:

        flash(
            "Please login to take the quiz.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM quiz_questions
    """)

    all_questions = cursor.fetchall()

    cursor.close()
    conn.close()

    # Select maximum 8 questions
    question_count = min(
        8,
        len(all_questions)
    )

    questions = random.sample(
        all_questions,
        question_count
    )

    # Store question IDs so the submitted quiz
    # is scored correctly.
    session["quiz_question_ids"] = [
        question["id"]
        for question in questions
    ]

    return render_template(
        "quiz.html",
        questions=questions
    )


@quiz_bp.route(
    "/quiz/submit",
    methods=["POST"]
)
def submit_quiz():

    if "user" not in session:

        flash(
            "Please login first.",
            "warning"
        )

        return redirect(
            url_for("auth.login")
        )

    question_ids = session.get(
        "quiz_question_ids",
        []
    )

    if not question_ids:

        flash(
            "Please start the quiz first.",
            "warning"
        )

        return redirect(
            url_for("quiz.quiz")
        )

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    placeholders = ",".join(
        ["%s"] * len(question_ids)
    )

    query = f"""
        SELECT *
        FROM quiz_questions
        WHERE id IN ({placeholders})
    """

    cursor.execute(
        query,
        tuple(question_ids)
    )

    questions = cursor.fetchall()

    score = 0

    for question in questions:

        submitted_answer = request.form.get(
            f"q_{question['id']}"
        )

        correct_answer = question[
            "correct_answer"
        ]

        if submitted_answer == correct_answer:
            score += 1

    total = len(questions)

    user_id = session["user"]["id"]

    # Save result
    cursor.execute("""
        INSERT INTO quiz_results
        (
            user_id,
            score,
            total
        )
        VALUES
        (%s, %s, %s)
    """, (
        user_id,
        score,
        total
    ))

    # 5 eco points for every correct answer
    points = score * 5

    cursor.execute("""
        UPDATE users
        SET eco_points = eco_points + %s
        WHERE id = %s
    """, (
        points,
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    session.pop(
        "quiz_question_ids",
        None
    )

    return render_template(
        "quiz_result.html",
        score=score,
        total=total,
        points=points
    )