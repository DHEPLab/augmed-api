from src import db


class FactRelationship(db.Model):
    __tablename__ = "fact_relationship"

    domain_concept_id_1 = db.Column(db.Integer, nullable=False)
    fact_id_1 = db.Column(db.Integer, nullable=False, primary_key=True)
    domain_concept_id_2 = db.Column(db.Integer, nullable=False)
    fact_id_2 = db.Column(db.Integer, nullable=False, primary_key=True)
    relationship_concept_id = db.Column(db.Integer, nullable=False)
