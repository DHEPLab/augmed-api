from src import db


class Provider(db.Model):
    __tablename__ = "provider"

    provider_id = db.Column(db.Integer, primary_key=True, nullable=False)
    provider_name = db.Column(db.String(255))
    npi = db.Column(db.String(20))
    dea = db.Column(db.String(20))
    specialty_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    care_site_id = db.Column(db.Integer, db.ForeignKey("care_site.care_site_id"))
    year_of_birth = db.Column(db.Integer)
    gender_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    provider_source_value = db.Column(db.String(50))
    specialty_source_value = db.Column(db.String(50))
    specialty_source_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )
    gender_source_value = db.Column(db.String(50))
    gender_source_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )

    # Relationships
    care_site = db.relationship(
        "CareSite", backref=db.backref("providers", lazy="dynamic")
    )
    specialty_concept = db.relationship(
        "Concept",
        foreign_keys=[specialty_concept_id],
        backref=db.backref("providers_as_specialty", lazy="dynamic"),
    )
    gender_concept = db.relationship(
        "Concept",
        foreign_keys=[gender_concept_id],
        backref=db.backref("providers_as_gender", lazy="dynamic"),
    )
