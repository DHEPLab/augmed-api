from src import db


class CohortDefinition(db.Model):
    __tablename__ = "cohort_definition"

    cohort_definition_id = db.Column(db.Integer, primary_key=True, nullable=False)
    cohort_definition_name = db.Column(db.String(255), nullable=False)
    cohort_definition_description = db.Column(db.Text)
    definition_type_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    cohort_definition_syntax = db.Column(db.Text)
    subject_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    cohort_initiation_date = db.Column(db.Date)
