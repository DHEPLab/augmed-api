from src import db


class DoseEra(db.Model):
    __tablename__ = "dose_era"

    dose_era_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    drug_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    unit_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    dose_value = db.Column(db.Numeric, nullable=False)
    dose_era_start_date = db.Column(db.Date, nullable=False)
    dose_era_end_date = db.Column(db.Date, nullable=False)

    # Relationships
    person = db.relationship("Person", backref=db.backref("dose_eras", lazy="dynamic"))
    drug_concept = db.relationship(
        "Concept",
        foreign_keys=[drug_concept_id],
        backref=db.backref("dose_eras_as_drug", lazy="dynamic"),
    )
    unit_concept = db.relationship(
        "Concept",
        foreign_keys=[unit_concept_id],
        backref=db.backref("dose_eras_as_unit", lazy="dynamic"),
    )
