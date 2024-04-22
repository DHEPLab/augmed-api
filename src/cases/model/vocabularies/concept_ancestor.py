from src import db


class ConceptAncestor(db.Model):
    __tablename__ = "concept_ancestor"

    ancestor_concept_id = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )
    descendant_concept_id = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )
    min_levels_of_separation = db.Column(db.Integer, nullable=False)
    max_levels_of_separation = db.Column(db.Integer, nullable=False)
