from src import db


class Domain(db.Model):
    __tablename__ = "domain"

    domain_id = db.Column(db.String(20), primary_key=True, nullable=False)
    domain_name = db.Column(db.String(255), nullable=False)
    domain_concept_id = db.Column(
        db.Integer, db.ForeignKey("concept.concept_id"), nullable=False
    )
