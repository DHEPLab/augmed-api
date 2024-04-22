from src import db


class Cohort(db.Model):
    __tablename__ = "cohort"

    cohort_definition_id = db.Column(
        db.Integer,
        db.ForeignKey("cohort_definition.cohort_definition_id"),
        primary_key=True,
        nullable=False,
    )
    subject_id = db.Column(
        db.Integer, db.ForeignKey("person.person_id"), primary_key=True, nullable=False
    )
    cohort_start_date = db.Column(db.Date, nullable=False)
    cohort_end_date = db.Column(db.Date, nullable=False)
