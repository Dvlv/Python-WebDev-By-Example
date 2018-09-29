from flask import render_template, request, flash

from models.runner import Runner
from web.views.blueprints import runner_blueprint
from web.views.runner.forms import RunnerForm


@runner_blueprint.route("/create", methods=["GET", "POST"])
def create():
    runner = Runner()
    form = RunnerForm(obj=runner)

    if request.method == "POST" and form.validate():
        runner.update_from_form(request.form)
        flash("Runner Created!")

    return render_template(
        "runner/create_form.html",
        form=form
    )


@runner_blueprint.route("/")
def index():
    all_runners = Runner.select()

    return render_template(
        "runner/index.html",
        all_runners=all_runners
    )