from src import db


class SourceToConceptMap(db.Model):
    __tablename__ = "source_to_concept_map"

    source_code = db.Column(db.String(50), primary_key=True, nullable=False)
    source_concept_id = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )
    source_vocabulary_id = db.Column(db.String(20), nullable=False)
    source_code_description = db.Column(db.String(255))
    target_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    target_vocabulary_id = db.Column(db.String(20), nullable=False)
    valid_start_date = db.Column(db.Date, nullable=False)
    valid_end_date = db.Column(db.Date, nullable=False)
    invalid_reason = db.Column(db.String(1))
