from src import db


class ConceptClass(db.Model):
    __tablename__ = "concept_class"

    concept_class_id = db.Column(db.String(20), primary_key=True, nullable=False)
    concept_class_name = db.Column(db.String(255), nullable=False)
    concept_class_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )

    # Relationship to Concept
    concept_class_concept = db.relationship(
        "Concept", backref=db.backref("concept_classes", lazy="dynamic")
    )
