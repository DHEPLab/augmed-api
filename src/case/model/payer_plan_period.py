from src import db


class PayerPlanPeriod(db.Model):
    __tablename__ = "payer_plan_period"

    payer_plan_period_id = db.Column(db.Integer, primary_key=True, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("person.person_id"), nullable=False)
    payer_plan_period_start_date = db.Column(db.Date, nullable=False)
    payer_plan_period_end_date = db.Column(db.Date, nullable=False)
    payer_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    payer_source_value = db.Column(db.String(50))
    payer_source_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    plan_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    plan_source_value = db.Column(db.String(50))
    plan_source_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    sponsor_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    sponsor_source_value = db.Column(db.String(50))
    sponsor_source_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )
    family_source_value = db.Column(db.String(50))
    stop_reason_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    stop_reason_source_value = db.Column(db.String(50))
    stop_reason_source_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id")
    )
