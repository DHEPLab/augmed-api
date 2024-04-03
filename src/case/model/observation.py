from src import db


class Observation(db.Model):
    __tablename__ = "observation"

    observation_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    observation_concept_id = db.Column(db.Integer, nullable=False)
    observation_date = db.Column(db.Date, nullable=False)
    observation_datetime = db.Column(db.TIMESTAMP)
    observation_type_concept_id = db.Column(db.Integer, nullable=False)
    value_as_number = db.Column(db.Numeric)
    value_as_string = db.Column(db.String(60))
    value_as_concept_id = db.Column(db.Integer)
    qualifier_concept_id = db.Column(db.Integer)
    unit_concept_id = db.Column(db.Integer)
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))
    visit_occurrence_id = db.Column(
        db.Integer, db.ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    visit_detail_id = db.Column(
        db.Integer, db.ForeignKey("visit_detail.visit_detail_id")
    )
    observation_source_value = db.Column(db.String(50))
    observation_source_concept_id = db.Column(db.Integer)
    unit_source_value = db.Column(db.String(50))
    qualifier_source_value = db.Column(db.String(50))
    value_source_value = db.Column(db.String(50))
    observation_event_id = db.Column(db.Integer)
    obs_event_field_concept_id = db.Column(db.Integer)

    # Define relationships
    person = db.relationship(
        "Person", backref=db.backref("observations", lazy="dynamic")
    )
    provider = db.relationship(
        "Provider", backref=db.backref("observations", lazy="dynamic")
    )
    visit_occurrence = db.relationship(
        "VisitOccurrence", backref=db.backref("observations", lazy="dynamic")
    )
    visit_detail = db.relationship(
        "VisitDetail", backref=db.backref("observations", lazy="dynamic")
    )
