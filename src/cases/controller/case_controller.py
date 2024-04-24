from flask import Blueprint, jsonify

from src import db
from src.cases.repository.concept_repository import ConceptRepository
from src.cases.repository.drug_exposure_repository import \
    DrugExposureRepository
from src.cases.repository.measurement_repository import MeasurementRepository
from src.cases.repository.observation_repository import ObservationRepository
from src.cases.repository.person_repository import PersonRepository
from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.cases.service.case_service import CaseService
from src.common.model.ApiResponse import ApiResponse
from src.user.repository.configuration_repository import \
    ConfigurationRepository

case_blueprint = Blueprint("case", __name__)
visit_occurrence_repository = VisitOccurrenceRepository(db.session)
concept_repository = ConceptRepository(db.session)
measurement_repository = MeasurementRepository(db.session)
observation_repository = ObservationRepository(db.session)
person_repository = PersonRepository(db.session)
drug_exposure_repository = DrugExposureRepository(db.session)
configuration_repository = ConfigurationRepository(db.session)
case_service = CaseService(
    visit_occurrence_repository=visit_occurrence_repository,
    concept_repository=concept_repository,
    measurement_repository=measurement_repository,
    observation_repository=observation_repository,
    person_repository=person_repository,
    drug_exposure_repository=drug_exposure_repository,
    configuration_repository=configuration_repository,
)


@case_blueprint.route("/cases/<int:case_id>", methods=["GET"])
# @jwt_validation_required()
def get_case_detail(case_id):
    case_review = case_service.get_case_review(case_id)
    return jsonify(ApiResponse.success(case_review)), 200
