from src import db


class CDMSource(db.Model):
    __tablename__ = "cdm_source"

    # While not explicitly defined as a primary key in the given schema,
    # we assume an ID field for ORM purposes; you might adjust based on your database's requirements.
    id = db.Column(db.Integer, primary_key=True)
    cdm_source_name = db.Column(db.String(255), nullable=False)
    cdm_source_abbreviation = db.Column(db.String(25), nullable=False)
    cdm_holder = db.Column(db.String(255), nullable=False)
    source_description = db.Column(db.Text)
    source_documentation_reference = db.Column(db.String(255))
    cdm_etl_reference = db.Column(db.String(255))
    source_release_date = db.Column(db.Date, nullable=False)
    cdm_release_date = db.Column(db.Date, nullable=False)
    cdm_version = db.Column(db.String(10))
    cdm_version_concept_id = db.Column(db.Integer, nullable=False)
    vocabulary_version = db.Column(db.String(20), nullable=False)

    # Relationships - assuming a Concept model exists for cdm_version_concept_id
    cdm_version_concept = db.relationship(
        "Concept", backref=db.backref("cdm_sources", lazy="dynamic")
    )
