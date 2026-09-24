from flask import (
    Blueprint,
    render_template,
    request,
    abort
)

from flask import current_app
from database.db import get_connection


awareness_bp = Blueprint(
    "awareness",
    __name__
)


@awareness_bp.route("/awareness")
def awareness():

    category = request.args.get(
        "category",
        ""
    ).strip()

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    if category:

        cursor.execute("""
            SELECT *
            FROM awareness
            WHERE category = %s
            ORDER BY id DESC
        """, (category,))

    else:

        cursor.execute("""
            SELECT *
            FROM awareness
            ORDER BY id DESC
        """)

    articles = cursor.fetchall()

    # Get available categories
    cursor.execute("""
        SELECT DISTINCT category
        FROM awareness
        ORDER BY category
    """)

    categories = [
        row["category"]
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return render_template(
        "awareness.html",
        articles=articles,
        categories=categories,
        selected_category=category
    )


@awareness_bp.route("/awareness/<int:article_id>")
def article(article_id):

    conn = get_connection(current_app)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM awareness
        WHERE id = %s
    """, (article_id,))

    article_data = cursor.fetchone()

    cursor.close()
    conn.close()

    if not article_data:
        abort(404)

    return render_template(
        "article.html",
        article=article_data
    )