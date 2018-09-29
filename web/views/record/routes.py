from flask import render_template, request, flash

from models.record import Record
from web.views.blueprints import record_blueprint
from web.views.record.forms import RecordForm


@record_blueprint.route("/create", methods=["GET", "POST"])
def create():
    record = Record()
    form = RecordForm(obj=record)

    if request.method == "POST" and form.validate():
        record.update_from_form(request.form)
        flash("Record Created!")

    return render_template(
        "record/create_form.html",
        form=form
    )


@record_blueprint.route("/")
def index():
    all_records = Record.select()

    return render_template(
        "record/index.html",
        all_records=all_records
    )