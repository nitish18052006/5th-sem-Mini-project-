from flask import (
    Blueprint,
    render_template,
    request
)

from ai.classifier import classify_environmental_issue


assistant_bp = Blueprint(
    "assistant",
    __name__
)


@assistant_bp.route(
    "/assistant",
    methods=["GET", "POST"]
)
def assistant():

    result = None
    user_text = ""

    if request.method == "POST":

        user_text = request.form.get(
            "problem",
            ""
        ).strip()

        if user_text:

            result = classify_environmental_issue(
                user_text
            )

    return render_template(
        "assistant.html",
        result=result,
        user_text=user_text
    )