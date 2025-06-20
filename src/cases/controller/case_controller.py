from flask import Blueprint, jsonify

from src import db
from src.answer.repository.answer_repository import AnswerRepository
from src.cases.repository.concept_repository import ConceptRepository
from src.cases.repository.drug_exposure_repository import DrugExposureRepository
from src.cases.repository.measurement_repository import MeasurementRepository
from src.cases.repository.observation_repository import ObservationRepository
from src.cases.repository.person_repository import PersonRepository
from src.cases.repository.visit_occurrence_repository import VisitOccurrenceRepository
from src.cases.service.case_service import CaseService
from src.common.model.ApiResponse import ApiResponse
from src.common.repository.system_config_repository import SystemConfigRepository
from src.user.repository.display_config_repository import DisplayConfigRepository
from src.user.utils import auth_utils
from src.user.utils.auth_utils import jwt_validation_required

case_blueprint = Blueprint("case", __name__)
visit_occurrence_repository = VisitOccurrenceRepository(db.session)
concept_repository = ConceptRepository(db.session)
measurement_repository = MeasurementRepository(db.session)
observation_repository = ObservationRepository(db.session)
person_repository = PersonRepository(db.session)
drug_exposure_repository = DrugExposureRepository(db.session)
configuration_repository = DisplayConfigRepository(db.session)
system_config_repository = SystemConfigRepository(db.session)
diagose_repository = AnswerRepository(db.session)
case_service = CaseService(
    visit_occurrence_repository=visit_occurrence_repository,
    concept_repository=concept_repository,
    measurement_repository=measurement_repository,
    observation_repository=observation_repository,
    person_repository=person_repository,
    drug_exposure_repository=drug_exposure_repository,
    configuration_repository=configuration_repository,
    system_config_repository=system_config_repository,
    diagnose_repository=diagose_repository,
)


@case_blueprint.route("/case-reviews/<string:case_config_id>", methods=["GET"])
@jwt_validation_required()
def get_case_detail(case_config_id):
    case_review = case_service.get_case_review(case_config_id)
    return jsonify(ApiResponse.success(case_review)), 200


@case_blueprint.route("/cases", methods=["GET"])
@jwt_validation_required()
def get_cases_by_user():
    user_email = auth_utils.get_user_email_from_jwt()
    summaries = case_service.get_cases_by_user(user_email)
    return jsonify(ApiResponse.success(summaries)), 200
