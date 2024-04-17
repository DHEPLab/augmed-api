from src import db


class ConceptSynonym(db.Model):
    __tablename__ = "concept_synonym"

    concept_id = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )
    concept_synonym_name = db.Column(db.String(1000), primary_key=True, nullable=False)
    language_concept_id = db.Column(
        db.Integer,
        db.ForeignKey("concept.concept_id"),
        primary_key=True,
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint(
            "concept_id", "concept_synonym_name", "language_concept_id"
        ),
    )

    # Relationships
    concept = db.relationship(
        "Concept",
        foreign_keys=[concept_id],
        backref=db.backref("synonyms", lazy="dynamic"),
    )
    language_concept = db.relationship(
        "Concept",
        foreign_keys=[language_concept_id],
        backref=db.backref("synonym_languages", lazy="dynamic"),
    )
