from sqlalchemy import TIMESTAMP, Column, Date, ForeignKey, Integer, String

from src import db


class VisitOccurrence(db.Model):
    __tablename__ = "visit_occurrence"

    visit_occurrence_id = Column(Integer, primary_key=True, nullable=False)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    visit_concept_id = Column(Integer, nullable=False)
    visit_start_date = Column(Date, nullable=False)
    visit_start_datetime = Column(TIMESTAMP)
    visit_end_date = Column(Date, nullable=False)
    visit_end_datetime = Column(TIMESTAMP)
    visit_type_concept_id = Column(Integer, nullable=False)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    care_site_id = Column(Integer, ForeignKey("care_site.care_site_id"))
    visit_source_value = Column(String(50))
    visit_source_concept_id = Column(Integer)
    admitted_from_concept_id = Column(Integer)
    admitted_from_source_value = Column(String(50))
    discharged_to_concept_id = Column(Integer)
    discharged_to_source_value = Column(String(50))
    preceding_visit_occurrence_id = Column(
        Integer, ForeignKey("visit_occurrence.visit_occurrence_id")
    )

    # Relationships
    # person = relationship("Person", back_populates="visit_occurrences")
