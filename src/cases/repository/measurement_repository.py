from sqlalchemy import select

from src.cases.model.clinical_data.person.measurement import Measurement
from src.cases.model.vocabularies.concept_relationship import \
    ConceptRelationship


class MeasurementRepository:
    def __init__(self, session):
        self.session = session

    def get_measurements(self, visit_id: int, concept_ids):
        statement = (
            select(Measurement)
            .select_from(Measurement)
            .where(
                Measurement.measurement_concept_id.in_(concept_ids),
                Measurement.visit_occurrence_id == visit_id,
            )
        )
        return self.session.execute(statement).scalars().all()

    def get_measurements_of_parents(self, visit_id: int, parent_concept_ids):
        statement = (
            select(Measurement)
            .select_from(Measurement)
            .join(
                ConceptRelationship,
                Measurement.measurement_concept_id == ConceptRelationship.concept_id_2,
            )
            .where(
                Measurement.visit_occurrence_id == visit_id,
                ConceptRelationship.concept_id_1.in_(parent_concept_ids),
                ConceptRelationship.relationship_id.in_(
                    ["Subsumes", "Is characterized by"]
                ),
            )
        )
        return self.session.execute(statement).scalars().all()
