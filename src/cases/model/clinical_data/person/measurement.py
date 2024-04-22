from src import db


class Measurement(db.Model):
    __tablename__ = "measurement"

    measurement_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    measurement_concept_id = db.Column(db.Integer, nullable=False)
    measurement_date = db.Column(db.Date, nullable=False)
    measurement_datetime = db.Column(db.TIMESTAMP)
    measurement_time = db.Column(db.String(10))
    measurement_type_concept_id = db.Column(db.Integer, nullable=False)
    operator_concept_id = db.Column(db.Integer)
    value_as_number = db.Column(db.Numeric)
    value_as_concept_id = db.Column(db.Integer)
    unit_concept_id = db.Column(db.Integer)
    range_low = db.Column(db.Numeric)
    range_high = db.Column(db.Numeric)
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))
    visit_occurrence_id = db.Column(
        db.Integer, db.ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    visit_detail_id = db.Column(
        db.Integer, db.ForeignKey("visit_detail.visit_detail_id")
    )
    measurement_source_value = db.Column(db.String(50))
    measurement_source_concept_id = db.Column(db.Integer)
    unit_source_value = db.Column(db.String(50))
    unit_source_concept_id = db.Column(db.Integer)
    value_source_value = db.Column(db.String(50))
    measurement_event_id = db.Column(db.Integer)
    meas_event_field_concept_id = db.Column(db.Integer)
