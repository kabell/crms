from __future__ import annotations

import datetime
from typing import Any

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

db = SQLAlchemy()


class BaseModel(db.Model):  # type: ignore
    __abstract__ = True

    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(
        db.DateTime,
        onupdate=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow,
        index=True,
    )

    @classmethod
    def create(cls, *args: Any, commit: bool = False, **kwargs: Any) -> Any:
        instance = cls(*args, **kwargs)

        db.session.add(instance)

        if commit:
            db.session.commit()
        return instance


class User(BaseModel):  # type: ignore
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False)
    api_token = db.Column(db.String(255))
    days = db.relationship(
        "Day",
        backref=db.backref("day"),
        lazy="dynamic",
    )
    day_history = db.relationship(
        "DayHistory",
        backref=db.backref("day_history"),
        lazy="dynamic",
    )

    def is_active(self) -> bool:
        """True, as all users are active."""
        return True

    def get_id(self) -> int:
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self) -> bool:
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self) -> bool:
        """False, as anonymous users aren't supported."""
        return False

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class Day(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
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
        return self.date == datetime.date.today()

    def from_dict(self, form: dict) -> None:
        self.category = form["category"]
        self.menstrual = form["menstrual"]
        self.indicator = form["indicator"]
        self.color = form["color"]
        self.sensation = form["sensation"]
        self.frequency = form["frequency"]
        self.peak = form["peak"]
        self.day_count = form["day_count"]
        self.intercourse = form["intercourse"]
        self.new_cycle = form["new_cycle"]
        self.notes = form["notes"]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "menstrual": self.menstrual,
            "indicator": self.indicator,
            "color": self.color,
            "sensation": self.sensation,
            "frequency": self.frequency,
            "peak": self.peak,
            "day_count": self.day_count,
            "intercourse": self.intercourse,
            "new_cycle": self.new_cycle,
            "notes": self.notes,
            "date": self.date.isoformat() if self.date else None,
        }

    @classmethod
    def default(cls, user_id: int, day_date: datetime.date) -> Day:
        return cls(
            user_id=user_id,
            category="N/A",
            menstrual="N/A",
            indicator="N/A",
            color="N/A",
            sensation="N/A",
            frequency="N/A",
            peak=False,
            day_count=0,
            intercourse=False,
            new_cycle=False,
            notes="",
            date=day_date,
        )


class DayHistory(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
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

    @classmethod
    def from_day(cls, day: Day) -> DayHistory:
        return cls(
            user_id=day.user_id,
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
        )
