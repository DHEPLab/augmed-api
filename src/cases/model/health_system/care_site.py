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

    # Relationships
    # location = db.relationship(
    #     "Location", backref=db.backref("care_sites", lazy="dynamic")
    # )
    # place_of_service_concept = db.relationship(
    #     "Concept",
    #     foreign_keys=[place_of_service_concept_id],
    #     backref=db.backref("care_sites_as_place_of_service", lazy="dynamic"),
    # )
