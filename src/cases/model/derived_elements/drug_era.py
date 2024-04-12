from src import db


class DrugEra(db.Model):
    __tablename__ = "drug_era"

    drug_era_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    drug_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    drug_era_start_date = db.Column(db.Date, nullable=False)
    drug_era_end_date = db.Column(db.Date, nullable=False)
    drug_exposure_count = db.Column(db.Integer)
    gap_days = db.Column(db.Integer)

    # Relationships
    person = db.relationship("Person", backref=db.backref("drug_eras", lazy="dynamic"))
    drug_concept = db.relationship(
        "Concept", backref=db.backref("drug_eras_as_drug", lazy="dynamic")
    )
