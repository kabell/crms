from datetime import date, datetime, timedelta

from flask import Flask, Response, render_template, request, send_file

from crms import config
from crms.models import Day, DayHistory, db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
app.secret_key = config.SECRET_KEY.encode()

db.init_app(app)

with app.app_context():
    db.create_all()

values = {
    "category": {
        "red": "Menštruácia",
        "green": "Sucho",
        "gray": "Pred vrcholom",
        "lightgreen": "Po vrchole",
    },
    "menstrual": {
        "N/A": "Žiadne",
        "H": "H - Veľmi silná",
        "M": "M - Stredne silná",
        "L": "L - Slabá",
        "VL": "VL - Veľmi slabá",
        "B": "B - Hnedá (čierna)",
    },
    "indicator": {
        "N/A": "Žiadne",
        "0": "0 - Sucho",
        "2": "2 - Vlhko bez klzkosti",
        "2W": "2W - Mokro bez klzkosti",
        "4": "4 - Lesk be klzkosti",
        "6": "6 - Lepkavý (do 0.5cm)",
        "8": "8 - Ťahavý (1 - 2 cm)",
        "10": "10 - Elastický (>2.5 cm)",
        "10DL": "10DL - Vlhko s klzkosťou",
        "10SL": "10SL - Lesk s klzkosťou",
        "10WL": "10WL - Mokro s klzkosťou",
    },
    "color": {
        "N/A": "Žiadne",
        "B": "B - Hnedé alebo čierne krvácanie",
        "C": "C - Zakalený (alebo biely)",
        "CK": "CK - Zakalený/číry",
        "G": "G - Gumenný (ako lepidlo)",
        "K": "K - Číry",
        "L": "L - Klzký",
        "P": "P - Pastovitý (alebo krémový)",
        "Y": "Y - Žltý (aj slabožltý)",
    },
    "sensation": {
        "N/A": "Žiadne",
        "L": "L - Klzký",
        "G": "G - Gumenný (ako lepidlo)",
        "P": "P - Pastovitý (alebo krémový)",
    },
    "frequency": {
        "N/A": "Žiadne",
        "X1": "X1 - Raz za deň",
        "X2": "X2 - Dva krát za deň",
        "X3": "X3 - Tri krát za deň",
        "AD": "AD - Po celý deň",
    },
    "day_count": {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
    },
}


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    day_date = (
        date.fromisoformat(request.args["day"])
        if request.args.get("day")
        else date.today()
    )

    day = Day.query.filter_by(date=day_date).first()
    if not day:
        day = Day(
            category="red",
            menstrual="N/A",
            indicator="N/A",
            color="N/A",
            sensation="N/A",
            frequency="N/A",
            peak=False,
            day_count=0,
            intercourse=False,
            notes="",
            date=day_date,
            created=datetime.now(),
        )

    if request.method == "POST":
        day.from_dict(request.form)
        day_history = DayHistory.from_day(day)
        db.session.add(day_history)
        db.session.add(day)
        db.session.commit()

    return render_template(
        "day_form.j2",
        day=day,
        prev_day=day.date - timedelta(days=1),
        next_day=day.date + timedelta(days=1),
        values=values,
    )


@app.route("/view")
def view() -> str:
    days = (
        Day.query.where(Day.date > date.today() - timedelta(days=30))
        .order_by(Day.date)
        .all()
    )
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
    return render_template("view.j2", cycles=cycles)


@app.route("/sw.js")
def binary() -> Response:

    return send_file(
        "static/sw.js",
        download_name="sw.js",  # type: ignore
    )
