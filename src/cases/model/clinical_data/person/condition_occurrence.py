from sqlalchemy import TIMESTAMP, Column, Date, ForeignKey, Integer, String

from src import db


class ConditionOccurrence(db.Model):
    __tablename__ = "condition_occurrence"

    condition_occurrence_id = Column(Integer, primary_key=True, nullable=False)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    condition_concept_id = Column(Integer, nullable=False)
    condition_start_date = Column(Date, nullable=False)
    condition_start_datetime = Column(TIMESTAMP)
    condition_end_date = Column(Date)
    condition_end_datetime = Column(TIMESTAMP)
    condition_type_concept_id = Column(Integer, nullable=False)
    condition_status_concept_id = Column(Integer)
    stop_reason = Column(String(20))
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    visit_occurrence_id = Column(
        Integer, ForeignKey("visit_occurrence.visit_occurrence_id")
    )
    visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    condition_source_value = Column(String(50))
    condition_source_concept_id = Column(Integer)
    condition_status_source_value = Column(String(50))
