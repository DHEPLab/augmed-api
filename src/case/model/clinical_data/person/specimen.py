from src import db


class Specimen(db.Model):
    __tablename__ = "specimen"

    specimen_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    specimen_concept_id = db.Column(db.Integer, nullable=False)
    specimen_type_concept_id = db.Column(db.Integer, nullable=False)
    specimen_date = db.Column(db.Date, nullable=False)
    specimen_datetime = db.Column(db.TIMESTAMP)
    quantity = db.Column(db.Numeric)
    unit_concept_id = db.Column(db.Integer)
    anatomic_site_concept_id = db.Column(db.Integer)
    disease_status_concept_id = db.Column(db.Integer)
    specimen_source_id = db.Column(db.String(50))
    specimen_source_value = db.Column(db.String(50))
    unit_source_value = db.Column(db.String(50))
    anatomic_site_source_value = db.Column(db.String(50))
    disease_status_source_value = db.Column(db.String(50))

    # Relationship to the Person table
    person = db.relationship("Person", backref=db.backref("specimens", lazy="dynamic"))
