from src import db


class Note(db.Model):
    __tablename__ = "note"

    note_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    note_date = db.Column(db.Date, nullable=False)
    note_datetime = db.Column(db.TIMESTAMP)
    note_type_concept_id = db.Column(db.Integer, nullable=False)
    note_class_concept_id = db.Column(db.Integer, nullable=False)
    note_title = db.Column(db.String(250))
    note_text = db.Column(db.Text, nullable=False)
    encoding_concept_id = db.Column(db.Integer, nullable=False)
    language_concept_id = db.Column(db.Integer, nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))
    visit_occurrence_id = db.Column(
        db.Integer, db.ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    visit_detail_id = db.Column(
        db.Integer, db.ForeignKey("visit_detail.visit_detail_id")
    )
    note_source_value = db.Column(db.String(50))
    note_event_id = db.Column(db.Integer)
    note_event_field_concept_id = db.Column(db.Integer)

    # Relationships
    person = db.relationship("Person", backref=db.backref("notes", lazy="dynamic"))
    provider = db.relationship("Provider", back_populates="notes")
    visit_occurrence = db.relationship("VisitOccurrence", back_populates="notes")
    visit_detail = db.relationship("VisitDetail", back_populates="notes")


# Ensure the back_populates parameters are correctly defined in related models as well
