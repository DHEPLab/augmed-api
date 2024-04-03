from src import db


class Relationship(db.Model):
    __tablename__ = "relationship"

    relationship_id = db.Column(db.String(20), primary_key=True, nullable=False)
    relationship_name = db.Column(db.String(255), nullable=False)
    is_hierarchical = db.Column(db.String(1), nullable=False)
    defines_ancestry = db.Column(db.String(1), nullable=False)
    reverse_relationship_id = db.Column(db.String(20), nullable=False)
    relationship_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )

    # Relationships
    relationship_concept = db.relationship(
        "Concept", backref=db.backref("relationships", lazy="dynamic")
    )
