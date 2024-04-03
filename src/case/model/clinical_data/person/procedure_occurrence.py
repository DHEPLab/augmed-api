from src import db


class ProcedureOccurrence(db.Model):
    __tablename__ = "procedure_occurrence"

    procedure_occurrence_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    procedure_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    procedure_date = db.Column(db.Date, nullable=False)
    procedure_datetime = db.Column(db.TIMESTAMP)
    procedure_end_date = db.Column(db.Date)
    procedure_end_datetime = db.Column(db.TIMESTAMP)
    procedure_type_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
    modifier_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    quantity = db.Column(db.Integer)
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))
    visit_occurrence_id = db.Column(
        db.Integer, db.ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    visit_detail_id = db.Column(
        db.Integer, db.ForeignKey("visit_detail.visit_detail_id")
    )
    procedure_source_value = db.Column(db.String(50))
    procedure_source_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )
    modifier_source_value = db.Column(db.String(50))

    # Relationships
    person = db.relationship(
        "Person", backref=db.backref("procedure_occurrences", lazy="dynamic")
    )
    procedure_concept = db.relationship(
        "Concept", foreign_keys=[procedure_concept_id], backref="procedure_occurrences"
    )
    procedure_type_concept = db.relationship(
        "Concept",
        foreign_keys=[procedure_type_concept_id],
        backref="procedure_occurrences_as_type",
    )
    modifier_concept = db.relationship(
        "Concept",
        foreign_keys=[modifier_concept_id],
        backref="procedure_occurrences_as_modifier",
    )
    provider = db.relationship(
        "Provider", backref=db.backref("procedure_occurrences", lazy="dynamic")
    )
    visit_occurrence = db.relationship(
        "VisitOccurrence", backref=db.backref("procedure_occurrences", lazy="dynamic")
    )
    visit_detail = db.relationship(
        "VisitDetail", backref=db.backref("procedure_occurrences", lazy="dynamic")
    )
    procedure_source_concept = db.relationship(
        "Concept",
        foreign_keys=[procedure_source_concept_id],
        backref="procedure_occurrences_as_source",
    )
