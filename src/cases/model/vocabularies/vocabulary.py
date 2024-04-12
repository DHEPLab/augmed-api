from src import db


# TODO:recheck index with document
# TODO relationship concept
class Vocabulary(db.Model):
    __tablename__ = "vocabulary"

    vocabulary_id = db.Column(db.String(20), primary_key=True, nullable=False)
    vocabulary_name = db.Column(db.String(255), nullable=False)
    vocabulary_reference = db.Column(db.String(255))
    vocabulary_version = db.Column(db.String(255))
    vocabulary_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )

    # Relationship to Concept
    vocabulary_concept = db.relationship(
        "Concept", backref=db.backref("vocabularies", lazy="dynamic")
    )
