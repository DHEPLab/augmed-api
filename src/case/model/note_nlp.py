from src import db


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
