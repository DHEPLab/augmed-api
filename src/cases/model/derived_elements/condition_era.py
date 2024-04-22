from src import db


class ConditionEra(db.Model):
    __tablename__ = "condition_era"

    condition_era_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    condition_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    condition_era_start_date = db.Column(db.Date, nullable=False)
    condition_era_end_date = db.Column(db.Date, nullable=False)
    condition_occurrence_count = db.Column(db.Integer)
