from db import db


class UrlModel(db.Model):
    __tablename__ = "urls"

    short_url = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    url = db.Column(db.String(250), unique=False, nullable=False)
    created = db.Column(db.DateTime, unique=False, nullable=False)
    counter = db.Column(db.Integer, unique=False, nullable=False)
