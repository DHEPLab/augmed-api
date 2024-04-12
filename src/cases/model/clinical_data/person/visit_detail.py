from sqlalchemy import TIMESTAMP, Column, Date, ForeignKey, Integer, String

from src import db


class VisitDetail(db.Model):
    __tablename__ = "visit_detail"

    visit_detail_id = Column(Integer, primary_key=True, nullable=False)
    person_id = Column(Integer, ForeignKey("person.person_id"), nullable=False)
    visit_detail_concept_id = Column(Integer, nullable=False)
    visit_detail_start_date = Column(Date, nullable=False)
    visit_detail_start_datetime = Column(TIMESTAMP)
    visit_detail_end_date = Column(Date, nullable=False)
    visit_detail_end_datetime = Column(TIMESTAMP)
    visit_detail_type_concept_id = Column(Integer, nullable=False)
    provider_id = Column(Integer, ForeignKey("provider.provider_id"))
    care_site_id = Column(Integer, ForeignKey("care_site.care_site_id"))
    visit_detail_source_value = Column(String(50))
    visit_detail_source_concept_id = Column(Integer)
    admitted_from_concept_id = Column(Integer)
    admitted_from_source_value = Column(String(50))
    discharged_to_source_value = Column(String(50))
    discharged_to_concept_id = Column(Integer)
    preceding_visit_detail_id = Column(
        Integer, ForeignKey("visit_detail.visit_detail_id")
    )
    parent_visit_detail_id = Column(Integer, ForeignKey("visit_detail.visit_detail_id"))
    visit_occurrence_id = Column(
        Integer, ForeignKey("visit_occurrence.visit_occurrence_id")
    )
