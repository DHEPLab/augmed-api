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
