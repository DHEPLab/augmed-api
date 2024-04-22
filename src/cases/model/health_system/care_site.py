from src import db


class CareSite(db.Model):
    __tablename__ = "care_site"

    care_site_id = db.Column(db.Integer, primary_key=True, nullable=False)
    care_site_name = db.Column(db.String(255))
    place_of_service_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )
    location_id = db.Column(db.Integer, db.ForeignKey("location.location_id"))
    care_site_source_value = db.Column(db.String(50))
    place_of_service_source_value = db.Column(db.String(50))
