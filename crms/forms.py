# pylint:disable=unused-argument
from typing import Optional

from wtforms import (
    BooleanField,
    Form,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    validators,
)

from crms.models import User

category = {
    "red": "Menštruácia",
    "green": "Sucho",
    "gray": "Pred vrcholom",
    "lightgreen": "Po vrchole",
}
menstrual = {
    "N/A": "Žiadne",
    "H": "H - Veľmi silná",
    "M": "M - Stredne silná",
    "L": "L - Slabá",
    "VL": "VL - Veľmi slabá",
    "B": "B - Hnedá (čierna)",
}
indicator = {
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
    "?X?": "?X? - Ani srnka netuší",
}
color = {
    "N/A": "Žiadne",
    "B": "B - Hnedé alebo čierne krvácanie",
    "C": "C - Zakalený (alebo biely)",
    "CK": "CK - Zakalený/číry",
    "G": "G - Gumenný (ako lepidlo)",
    "K": "K - Číry",
    "L": "L - Klzký",
    "P": "P - Pastovitý (alebo krémový)",
    "Y": "Y - Žltý (aj slabožltý)",
}
sensation = {
    "N/A": "Žiadne",
    "L": "L - Klzký",
    "G": "G - Gumenný (ako lepidlo)",
    "P": "P - Pastovitý (alebo krémový)",
}
frequency = {
    "N/A": "Žiadne",
    "X1": "X1 - Raz za deň",
    "X2": "X2 - Dva krát za deň",
    "X3": "X3 - Tri krát za deň",
    "AD": "AD - Po celý deň",
}
day_count = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
}


class RegistrationForm(Form):
    username = StringField("Meno", [validators.Length(min=4, max=25)])
    password = PasswordField(
        "Heslo",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Heslá sa musia zhodovať"),
        ],
    )
    confirm = PasswordField("Heslo znovu")

    def validate(self, extra_validators: Optional[list] = None) -> bool:
        if not super().validate():
            return False
        user = User.query.filter_by(name=self.username.data).first()
        if user:
            self.username.errors.append("Užívateľ už existuje")
            return False
        return True


class LoginForm(Form):
    username = StringField("Meno", [validators.DataRequired()])
    password = PasswordField(
        "Heslo",
        [
            validators.DataRequired(),
        ],
    )

    def validate(self, extra_validators: Optional[list] = None) -> bool:
        if not super().validate():
            return False
        user = User.query.filter_by(name=self.username.data).first()
        if not user:
            self.username.errors.append("Užívateľ neexistuje")
            return False
        if not user.verify_password(self.password.data):
            self.password.errors.append("Zlé heslo")
            return False
        return True


class DayForm(Form):
    category = RadioField(
        "Kategória", choices=category.items(), validators=[validators.DataRequired()]
    )
    menstrual = SelectField("Menštruácia", choices=menstrual.items())
    sensation = SelectField("Pocit", choices=sensation.items())
    indicator = SelectField("Pozorovanie", choices=indicator.items())
    color = SelectField("Farba", choices=color.items())
    frequency = SelectField("Frekvencia", choices=frequency.items())
    peak = BooleanField("Vrchol")
    day_count = SelectField("Počet dní", choices=day_count.items())
    intercourse = BooleanField("Pohlavný styk")
    new_cycle = BooleanField("Nový cyklus")
    notes = StringField("Poznámka")
