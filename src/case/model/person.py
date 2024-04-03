from sqlalchemy import TIMESTAMP, Column, Integer, String

from src import db


class Person(db.Model):
    __tablename__ = "person"

    person_id = Column(Integer, primary_key=True, nullable=False)
    gender_concept_id = Column(Integer, nullable=False)
    year_of_birth = Column(Integer, nullable=False)
    month_of_birth = Column(Integer)
    day_of_birth = Column(Integer)
    birth_datetime = Column(TIMESTAMP)
    race_concept_id = Column(Integer, nullable=False)
    ethnicity_concept_id = Column(Integer, nullable=False)
    location_id = Column(Integer)
    provider_id = Column(Integer)
    care_site_id = Column(Integer)
    person_source_value = Column(String(50))
    gender_source_value = Column(String(50))
    gender_source_concept_id = Column(Integer)
    race_source_value = Column(String(50))
    race_source_concept_id = Column(Integer)
    ethnicity_source_value = Column(String(50))
    ethnicity_source_concept_id = Column(Integer)
