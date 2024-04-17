from src import db


class DrugExposure(db.Model):
    __tablename__ = "drug_exposure"

    drug_exposure_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    drug_concept_id = db.Column(db.Integer, nullable=False)
    drug_exposure_start_date = db.Column(db.Date, nullable=False)
    drug_exposure_start_datetime = db.Column(db.TIMESTAMP)
    drug_exposure_end_date = db.Column(db.Date, nullable=False)
    drug_exposure_end_datetime = db.Column(db.TIMESTAMP)
    verbatim_end_date = db.Column(db.Date)
    drug_type_concept_id = db.Column(db.Integer, nullable=False)
    stop_reason = db.Column(db.String(20))
    refills = db.Column(db.Integer)
    quantity = db.Column(db.Numeric)
    days_supply = db.Column(db.Integer)
    sig = db.Column(db.Text)
    route_concept_id = db.Column(db.Integer)
    lot_number = db.Column(db.String(50))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))
    visit_occurrence_id = db.Column(
        db.Integer, db.ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    visit_detail_id = db.Column(
        db.Integer, db.ForeignKey("visit_detail.visit_detail_id")
    )
    drug_source_value = db.Column(db.String(50))
    drug_source_concept_id = db.Column(db.Integer)
    route_source_value = db.Column(db.String(50))
    dose_unit_source_value = db.Column(db.String(50))

    # Define relationships
    # person = db.relationship("Person", backref=db.backref("drug_exposures", lazy=True))
    # provider = db.relationship(
    #     "Provider", backref=db.backref("drug_exposures", lazy=True)
    # )
    # visit_occurrence = db.relationship(
    #     "VisitOccurrence", backref=db.backref("drug_exposures", lazy=True)
    # )
    # visit_detail = db.relationship(
    #     "VisitDetail", backref=db.backref("drug_exposures", lazy=True)
    # )
