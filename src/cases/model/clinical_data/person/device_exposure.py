from src import db


class DeviceExposure(db.Model):
    __tablename__ = "device_exposure"

    device_exposure_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    device_concept_id = db.Column(db.Integer, nullable=False)
    device_exposure_start_date = db.Column(db.Date, nullable=False)
    device_exposure_start_datetime = db.Column(db.TIMESTAMP)
    device_exposure_end_date = db.Column(db.Date)
    device_exposure_end_datetime = db.Column(db.TIMESTAMP)
    device_type_concept_id = db.Column(db.Integer, nullable=False)
    unique_device_id = db.Column(db.String(255))
    production_id = db.Column(db.String(255))
    quantity = db.Column(db.Integer)
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))
    visit_occurrence_id = db.Column(
        db.Integer, db.ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    visit_detail_id = db.Column(
        db.Integer, db.ForeignKey("visit_detail.visit_detail_id")
    )
    device_source_value = db.Column(db.String(50))
    device_source_concept_id = db.Column(db.Integer)
    unit_concept_id = db.Column(db.Integer)
    unit_source_value = db.Column(db.String(50))
    unit_source_concept_id = db.Column(db.Integer)

    # Define relationships
    person = db.relationship(
        "Person", backref=db.backref("device_exposures", lazy="dynamic")
    )
    provider = db.relationship(
        "Provider", backref=db.backref("device_exposures", lazy="dynamic")
    )
    visit_occurrence = db.relationship(
        "VisitOccurrence", backref=db.backref("device_exposures", lazy="dynamic")
    )
    visit_detail = db.relationship(
        "VisitDetail", backref=db.backref("device_exposures", lazy="dynamic")
    )
