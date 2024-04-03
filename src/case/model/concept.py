from src import db


class Concept(db.Model):
    __tablename__ = "concept"

    concept_id = db.Column(db.Integer, primary_key=True, nullable=False)
    concept_name = db.Column(db.String(255), nullable=False)
    domain_id = db.Column(db.String(20), nullable=False)
    vocabulary_id = db.Column(db.String(20), nullable=False)
    concept_class_id = db.Column(db.String(20), nullable=False)
    standard_concept = db.Column(db.String(1))
    concept_code = db.Column(db.String(50), nullable=False)
    valid_start_date = db.Column(db.Date, nullable=False)
    valid_end_date = db.Column(db.Date, nullable=False)
    invalid_reason = db.Column(db.String(1))
