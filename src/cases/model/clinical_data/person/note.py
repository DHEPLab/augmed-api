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


class NoteNLP(db.Model):
    __tablename__ = "note_nlp"

    note_nlp_id = db.Column(db.Integer, primary_key=True, nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey("note.note_id"), nullable=False)
    section_concept_id = db.Column(db.Integer)
    snippet = db.Column(db.String(250))
    offset = db.Column(db.String(50))
    lexical_variant = db.Column(db.String(250), nullable=False)
    note_nlp_concept_id = db.Column(db.Integer)
    note_nlp_source_concept_id = db.Column(db.Integer)
    nlp_system = db.Column(db.String(250), nullable=False)
    nlp_date = db.Column(db.Date, nullable=False)
    nlp_datetime = db.Column(db.TIMESTAMP)
    term_exists = db.Column(db.String(1))
    term_temporal = db.Column(db.String(50))
    term_modifiers = db.Column(db.String(2000))
    # Relationship to the Note table
    note = db.relationship("Note", backref=db.backref("note_nlps", lazy="dynamic"))
