from src import db


class Cost(db.Model):
    __tablename__ = "cost"

    cost_id = db.Column(db.Integer, primary_key=True, nullable=False)
    cost_event_id = db.Column(db.Integer, nullable=False)
    cost_domain_id = db.Column(db.String(20), nullable=False)
    cost_type_concept_id = db.Column(db.Integer, nullable=False)
    currency_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    total_charge = db.Column(db.Numeric)
    total_cost = db.Column(db.Numeric)
    total_paid = db.Column(db.Numeric)
    paid_by_payer = db.Column(db.Numeric)
    paid_by_patient = db.Column(db.Numeric)
    paid_patient_copay = db.Column(db.Numeric)
    paid_patient_coinsurance = db.Column(db.Numeric)
    paid_patient_deductible = db.Column(db.Numeric)
    paid_by_primary = db.Column(db.Numeric)
    paid_ingredient_cost = db.Column(db.Numeric)
    paid_dispensing_fee = db.Column(db.Numeric)
    payer_plan_period_id = db.Column(
        db.Integer, db.ForeignKey("payer_plan_period.payer_plan_period_id")
    )
    amount_allowed = db.Column(db.Numeric)
    revenue_code_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    revenue_code_source_value = db.Column(db.String(50))
    drg_concept_id = db.Column(db.Integer, db.ForeignKey("concept.concept_id"))
    drg_source_value = db.Column(db.String(3))

    # Relationships
    currency_concept = db.relationship(
        "Concept",
        foreign_keys=[currency_concept_id],
        backref=db.backref("costs_as_currency", lazy="dynamic"),
    )
    revenue_code_concept = db.relationship(
        "Concept",
        foreign_keys=[revenue_code_concept_id],
        backref=db.backref("costs_as_revenue_code", lazy="dynamic"),
    )
    drg_concept = db.relationship(
        "Concept",
        foreign_keys=[drg_concept_id],
        backref=db.backref("costs_as_drg", lazy="dynamic"),
    )
    payer_plan_period = db.relationship(
        "PayerPlanPeriod", backref=db.backref("costs", lazy="dynamic")
    )
