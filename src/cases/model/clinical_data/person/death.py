from src import db


class Death(db.Model):
    __tablename__ = "death"

    person_id = db.Column(
        db.Integer, db.ForeignKey("person.person_id"), primary_key=True, nullable=False
    )
    death_date = db.Column(db.Date, nullable=False)
    death_datetime = db.Column(db.TIMESTAMP)
    death_type_concept_id = db.Column(db.Integer)
    cause_concept_id = db.Column(db.Integer)
    cause_source_value = db.Column(db.String(50))
    cause_source_concept_id = db.Column(db.Integer)
