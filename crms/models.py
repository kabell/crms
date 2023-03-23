from __future__ import annotations

from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Day(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32))
    menstrual = db.Column(db.String(32))
    indicator = db.Column(db.String(32))
    color = db.Column(db.String(32))
    sensation = db.Column(db.String(32))
    frequency = db.Column(db.String(32))
    peak = db.Column(db.Boolean)
    day_count = db.Column(db.Integer)
    intercourse = db.Column(db.Boolean)
    notes = db.Column(db.String(512))
    date = db.Column(db.Date, unique=True)
    new_cycle = db.Column(db.Boolean)
    created = db.Column(db.DateTime)

    def format(self) -> str:
        menstrual = self.menstrual if self.menstrual != "N/A" else ""
        observation = self.indicator if self.indicator != "N/A" else ""
        observation += self.color if self.color != "N/A" else ""
        observation += self.sensation if self.sensation != "N/A" else ""

        frequency = self.frequency if self.frequency != "N/A" else ""

        intercourse = "I" if self.intercourse else ""

        res = menstrual
        res = self.merge(res, observation, ";")
        res = self.merge(res, frequency, "-")
        res = self.merge(res, intercourse, " ")

        return res

    def merge(self, s1: str, s2: str, sep: str) -> str:
        if s1 and s2:
            return s1 + sep + s2
        return s1 or s2

    def format_peak(self) -> str:
        if self.peak:
            return "P"
        if self.day_count:
            return str(self.day_count)
        return ""

    def is_today(self) -> bool:
        return self.date == date.today()

    def from_dict(self, form: dict) -> None:
        self.category = form["category"]
        self.menstrual = form["menstrual"]
        self.indicator = form["indicator"]
        self.color = form["color"]
        self.sensation = form["sensation"]
        self.frequency = form["frequency"]
        self.peak = "peak" in form
        self.day_count = form["day_count"]
        self.intercourse = "intercourse" in form
        self.new_cycle = "new_cycle" in form
        self.notes = form["notes"]


class DayHistory(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(32))
    menstrual = db.Column(db.String(32))
    indicator = db.Column(db.String(32))
    color = db.Column(db.String(32))
    sensation = db.Column(db.String(32))
    frequency = db.Column(db.String(32))
    peak = db.Column(db.Boolean)
    day_count = db.Column(db.Integer)
    intercourse = db.Column(db.Boolean)
    notes = db.Column(db.String(512))
    date = db.Column(db.Date)
    new_cycle = db.Column(db.Boolean)
    created = db.Column(db.DateTime)

    @classmethod
    def from_day(cls, day: Day) -> DayHistory:
        return cls(
            category=day.category,
            menstrual=day.menstrual,
            indicator=day.indicator,
            color=day.color,
            sensation=day.sensation,
            frequency=day.frequency,
            peak=day.peak,
            day_count=day.day_count,
            intercourse=day.intercourse,
            notes=day.notes,
            date=day.date,
            new_cycle=day.new_cycle,
            created=datetime.now(),
        )
