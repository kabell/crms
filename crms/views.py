import csv
import json
from datetime import date, timedelta
from io import StringIO
from typing import Union

from flask import (
    Blueprint,
    Response,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.datastructures import MultiDict
from werkzeug.security import generate_password_hash

from crms.forms import DayForm, LoginForm, RegistrationForm
from crms.models import Day, DayHistory, User, db

app = Blueprint("", __name__, template_folder="templates")


def get_day_date() -> date:
    return (
        date.fromisoformat(request.args["day"])
        if request.args.get("day")
        else date.today()
    )


@app.route("/", methods=["GET", "POST"])
@login_required
def index() -> str:
    day_date = get_day_date()

    form = DayForm(request.form)

    day = current_user.days.filter_by(date=day_date).first() or Day.default(
        current_user.id, day_date
    )

    saved = False
    if request.method == "POST" and form.validate():
        day.from_dict(form.data)
        day_history = DayHistory.from_day(day)
        db.session.add(day_history)
        db.session.add(day)
        db.session.commit()
        saved = True
    else:
        form = DayForm(MultiDict(day.to_dict()))

    return render_template(
        "day.j2",
        day=day,
        day_date=day.date,
        prev_day=day.date - timedelta(days=1),
        next_day=day.date + timedelta(days=1),
        saved=saved,
        form=form,
    )


@app.route("/overview")
@login_required
def overview() -> str:
    days = current_user.days.order_by(Day.date).all()
    cycles: list[list[Day]] = []
    cur_cycle: list[Day] = []
    for day in days:
        if day.new_cycle:
            if cur_cycle:
                cycles.append(cur_cycle)
                cur_cycle = []
        if cur_cycle:
            cur_cycle += [None for _ in range((day.date - cur_cycle[-1].date).days - 1)]
        cur_cycle.append(day)
    if cur_cycle:
        cycles.append(cur_cycle)
    return render_template(
        "overview.j2", cycles=reversed(cycles), day_date=get_day_date()
    )


@app.route("/sw.js")
def binary() -> Response:

    return send_file(
        "static/sw.js",
        download_name="sw.js",  # type: ignore
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> Union[Response, str]:
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(name=form.username.data).first()
        login_user(user, remember=True)

        return redirect(url_for("index"))

    return render_template("login.j2", form=form)


@app.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm(request.form)

    if request.method == "POST" and form.validate():
        User.create(
            name=form.username.data,
            password=generate_password_hash(form.password.data, method="sha256"),
            commit=True,
        )
        return redirect(url_for("login"))

    return render_template("register.j2", form=form)


@app.route("/register_post", methods=["POST"])
def register_post() -> Union[Response, str]:
    name = request.form.get("name")
    password = request.form.get("password")

    user = User.query.filter_by(name=name).first()
    if user:
        return render_template("register.j2")

    User.create(
        name=name,
        password=generate_password_hash(password, method="sha256"),
        commit=True,
    )

    return redirect(url_for("index"))


@app.route("/logout", methods=["GET"])
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for("login"))


@app.route("/export", methods=["GET"])
@login_required
def export_json() -> Response:
    data = json.dumps([day.to_dict() for day in Day.query.order_by(Day.date).all()])

    return Response(
        data,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=crms.json"},
    )


@app.route("/export_csv", methods=["GET"])
@login_required
def export_csv() -> Response:
    f = StringIO()
    writer = csv.DictWriter(f, fieldnames=Day().to_dict().keys())
    writer.writeheader()
    for day in Day.query.order_by(Day.date).all():
        writer.writerow(day.to_dict())

    return Response(
        f.getvalue().encode(),
        mimetype="application/csv",
        headers={"Content-Disposition": "attachment;filename=crms.csv"},
    )
