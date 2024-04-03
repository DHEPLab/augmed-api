from src import db


class Location(db.Model):
    __tablename__ = "location"

    location_id = db.Column(db.Integer, primary_key=True, nullable=False)
    address_1 = db.Column(db.String(50))
    address_2 = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(9))
    county = db.Column(db.String(20))
    location_source_value = db.Column(db.String(50))
    country_concept_id = db.Column(db.Integer)
    country_source_value = db.Column(db.String(80))
    latitude = db.Column(db.Numeric)
    longitude = db.Column(db.Numeric)
