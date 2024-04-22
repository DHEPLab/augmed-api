from src import db


class Metadata(db.Model):
    __tablename__ = "metadata"

    metadata_id = db.Column(db.Integer, primary_key=True, nullable=False)
    metadata_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    metadata_type_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    name = db.Column(db.String(250), nullable=False)
    value_as_string = db.Column(db.String(250))
    value_as_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    value_as_number = db.Column(db.Numeric)
    metadata_date = db.Column(db.Date)
    metadata_datetime = db.Column(db.TIMESTAMP)
