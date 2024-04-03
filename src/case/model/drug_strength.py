from src import db


class DrugStrength(db.Model):
    __tablename__ = "drug_strength"

    drug_concept_id = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )
    ingredient_concept_id = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )
    amount_value = db.Column(db.Numeric)
    amount_unit_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    numerator_value = db.Column(db.Numeric)
    numerator_unit_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )
    denominator_value = db.Column(db.Numeric)
    denominator_unit_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )
    box_size = db.Column(db.Integer)
    valid_start_date = db.Column(db.Date, nullable=False)
    valid_end_date = db.Column(db.Date, nullable=False)
    invalid_reason = db.Column(db.String(1))

    # Relationships
    drug_concept = db.relationship(
        "Concept", foreign_keys=[drug_concept_id], backref="drug_strengths_as_drug"
    )
    ingredient_concept = db.relationship(
        "Concept",
        foreign_keys=[ingredient_concept_id],
        backref="drug_strengths_as_ingredient",
    )
    amount_unit_concept = db.relationship(
        "Concept",
        foreign_keys=[amount_unit_concept_id],
        backref="drug_strengths_as_amount_unit",
    )
    numerator_unit_concept = db.relationship(
        "Concept",
        foreign_keys=[numerator_unit_concept_id],
        backref="drug_strengths_as_numerator_unit",
    )
    denominator_unit_concept = db.relationship(
        "Concept",
        foreign_keys=[denominator_unit_concept_id],
        backref="drug_strengths_as_denominator_unit",
    )
