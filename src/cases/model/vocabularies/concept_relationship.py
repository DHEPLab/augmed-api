from src import db


class ConceptRelationship(db.Model):
    __tablename__ = "concept_relationship"

    concept_id_1 = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )
    concept_id_2 = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )
    relationship_id = db.Column(
        db.String(20),
        db.ForeignKey("relationship.relationship_id"),
        primary_key=True,
        nullable=False,
    )
    valid_start_date = db.Column(db.Date, nullable=False)
    valid_end_date = db.Column(db.Date, nullable=False)
    invalid_reason = db.Column(db.String(1))
