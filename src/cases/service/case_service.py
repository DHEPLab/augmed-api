from collections import defaultdict
from operator import itemgetter

from src.cases.controller.response.case_summary import CaseSummary
from src.cases.model.case import Case, TreeNode
from src.cases.repository.concept_repository import ConceptRepository
from src.cases.repository.drug_exposure_repository import \
    DrugExposureRepository
from src.cases.repository.measurement_repository import MeasurementRepository
from src.cases.repository.observation_repository import ObservationRepository
from src.cases.repository.person_repository import PersonRepository
from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.common.exception.BusinessException import (BusinessException,
                                                    BusinessExceptionEnum)
from src.common.repository.system_config_repository import \
    SystemConfigRepository
from src.diagnose.repository.diagnose_repository import DiagnoseRepository
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from src.user.utils.auth_utils import get_user_email_from_jwt


def group_by(source_list, key_selector):
    target_list = defaultdict(list)
    for item in source_list:
        target_list[key_selector(item)].append(item)
    return target_list


def get_value_of_rows(rows: list, get_func) -> str | None | list:
    if len(rows) == 1:
        return get_func(rows[0])
    result = []
    for row in rows:
        value = get_func(row)
        if value:
            result.append(value)
    return result


def is_leaf_node(config):
    return isinstance(config, list) | isinstance(config, int)


def get_age(person, visit_occurrence):
    return str(visit_occurrence.visit_start_date.year - person.year_of_birth)


def attach_style(display_configuration, case_details, important_infos):
    paths = display_configuration["path"].split(".")
    level = 0
    nodes = case_details
    while level < len(paths):
        found = False
        for node in nodes:
            if node.key == paths[level]:
                nodes = node.values
                level = level + 1
                found = True
                if level == len(paths):
                    node.style = display_configuration["style"]
                    if node.style.get("top") or node.style.get("top") == 0:
                        important_infos.append(
                            {
                                "key": "ignore" if level == 2 else node.key,
                                "values": node.values,
                                "weight": node.style["top"],
                            }
                        )
                break
        if not found:
            break


def add_if_value_present(data, node):
    if node.values:
        data.append(node)


class CaseService:
    def __init__(
        self,
        visit_occurrence_repository: VisitOccurrenceRepository,
        concept_repository: ConceptRepository,
        measurement_repository: MeasurementRepository,
        observation_repository: ObservationRepository,
        person_repository: PersonRepository,
        drug_exposure_repository: DrugExposureRepository,
        configuration_repository: ConfigurationRepository,
        system_config_repository: SystemConfigRepository,
        diagnose_repository: DiagnoseRepository,
    ):
        self.person = None
        self.visit_occurrence_repository = visit_occurrence_repository
        self.concept_repository = concept_repository
        self.measurement_repository = measurement_repository
        self.observation_repository = observation_repository
        self.person_repository = person_repository
        self.drug_exposure_repository = drug_exposure_repository
        self.configuration_repository = configuration_repository
        self.system_config_repository = system_config_repository
        self.diagnose_repository = diagnose_repository

    def get_case_detail(self, case_id):
        page_config = self.get_page_configuration()
        title_resolvers = {
            "BACKGROUND": self.get_nodes_of_background,
            "PATIENT COMPLAINT": self.get_nodes_of_observation,
            "PHYSICAL EXAMINATION": self.get_nodes_of_measurement,
        }
        data: list[TreeNode] = []
        for key, title_config in page_config.items():
            add_if_value_present(
                data, TreeNode(key, title_resolvers[key](case_id, title_config))
            )
        return data

    def get_nodes_of_measurement(self, case_id, title_config):
        data: list[TreeNode] = []
        for key, title_concept_ids in title_config.items():
            section_name = self.get_concept_name(title_concept_ids[0])
            parent_measurements = self.measurement_repository.get_measurements(
                case_id, title_concept_ids
            )
            if parent_measurements:
                data.append(
                    TreeNode(
                        section_name,
                        get_value_of_rows(
                            parent_measurements, self.get_value_of_measurement
                        ),
                    )
                )
            else:
                children_measurements = (
                    self.measurement_repository.get_measurements_of_parents(
                        case_id, title_concept_ids
                    )
                )
                parent_node = TreeNode(section_name, [])
                measurements_by_concept = group_by(
                    children_measurements, lambda m: m.measurement_concept_id
                )
                for concept_id, rows in measurements_by_concept.items():
                    parent_node.add_node(
                        TreeNode(
                            self.get_concept_name(concept_id),
                            get_value_of_rows(rows, self.get_value_of_measurement),
                        )
                    )
                add_if_value_present(data, parent_node)
        return data

    def get_value_of_measurement(self, measurement) -> str | None:
        value = None
        if measurement.value_as_number:
            value = str(measurement.value_as_number)
        elif measurement.value_as_concept_id:
            value = self.get_concept_name(measurement.value_as_concept_id)
        elif measurement.unit_source_value:
            value = measurement.unit_source_value
        if value and measurement.unit_concept_id:
            value = value + " " + self.get_concept_name(measurement.unit_concept_id)
        if value and measurement.operator_concept_id:
            value = self.get_concept_name(measurement.operator_concept_id) + " " + value
        return value

    def get_nodes_of_observation(self, case_id, title_config):
        data: list[TreeNode] = []
        for key, concept_type_ids in title_config.items():
            parent_node = TreeNode(key, [])
            observations = self.observation_repository.get_observations_by_type(
                case_id, concept_type_ids
            )
            observations_by_concept = group_by(
                observations, lambda o: o.observation_concept_id
            )
            for concept_id, rows in observations_by_concept.items():
                parent_node.add_node(
                    TreeNode(
                        self.get_concept_name(concept_id),
                        get_value_of_rows(rows, self.get_value_of_observation),
                    )
                )
            add_if_value_present(data, parent_node)
        return data

    def get_value_of_observation(self, observation) -> str | None:
        value = None
        if observation.value_as_string:
            value = observation.value_as_string
        elif observation.value_as_number:
            value = str(observation.value_as_number)
        elif observation.value_as_concept_id:
            value = self.get_concept_name(observation.value_as_concept_id)
        elif observation.unit_source_value:
            value = observation.unit_source_value
        if value and observation.unit_concept_id:
            value = value + " " + self.get_concept_name(observation.unit_concept_id)
        if value and observation.qualifier_concept_id:
            value = (
                self.get_concept_name(observation.qualifier_concept_id) + " : " + value
            )
        return value

    def get_nodes_of_background(self, case_id, title_config):
        data: list[TreeNode] = [
            self.get_nodes_of_patient(case_id),
        ]
        for key, config in title_config.items():
            node = TreeNode(key, self.get_nodes_of_nested_fields(case_id, config))
            add_if_value_present(data, node)
        return data

    def get_nodes_of_patient(self, case_id):
        visit_occurrence = self.visit_occurrence_repository.get_visit_occurrence(
            case_id
        )
        person = self.person_repository.get_person(visit_occurrence.person_id)
        age = get_age(person, visit_occurrence)
        gender = self.get_concept_name(person.gender_concept_id)
        self.person = person
        return TreeNode(
            "Patient Demographics", [TreeNode("Age", age), TreeNode("Gender", gender)]
        )

    def get_nodes_of_nested_fields(self, case_id, config):
        if is_leaf_node(config):
            observations = self.observation_repository.get_observations_by_concept(
                case_id, config
            )
            return get_value_of_rows(observations, self.get_value_of_observation)
        data: list[TreeNode] = []
        for key, nested_config in config.items():
            node = TreeNode(
                key, self.get_nodes_of_nested_fields(case_id, nested_config)
            )
            add_if_value_present(data, node)
        return data

    def get_concept_name(self, concept_id):
        return self.concept_repository.get_concept(concept_id).concept_name

    def get_page_configuration(self):
        return self.system_config_repository.get_config_by_id("page_config").json_config

    def get_case_review(self, case_config_id):
        configuration = self.configuration_repository.get_configuration_by_id(
            case_config_id
        )
        current_user = get_user_email_from_jwt()
        if not configuration or configuration.user_email != current_user:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        path_configurations = configuration.path_config if configuration else None
        case_details = self.get_case_detail(configuration.case_id)

        important_infos = []
        if path_configurations:
            for item in path_configurations:
                if item.get("style"):
                    attach_style(item, case_details, important_infos)

        important_infos.sort(key=itemgetter("weight"))
        sorted_important_infos = map(
            lambda e: TreeNode(e["key"], e["values"]), important_infos
        )

        return Case(
            self.person.person_source_value,
            str(configuration.case_id),
            case_details,
            list(sorted_important_infos),
        )

    def __get_current_case_by_user(self, user_email) -> tuple:
        case_config_pairs = (
            self.configuration_repository.get_case_configurations_by_user(
                user_email=user_email
            )
        )
        completed_case_list = self.diagnose_repository.get_diagnosed_case_list_by_user(
            user_email=user_email
        )

        for case_id, config_id in case_config_pairs:
            if config_id not in completed_case_list:
                return case_id, config_id
        return None, None

    def get_cases_by_user(self, user_email) -> list[CaseSummary]:
        case_id, config_id = self.__get_current_case_by_user(user_email=user_email)
        if not case_id or not config_id:
            return []

        cases_summary_list = []
        page_config = self.get_page_configuration()
        chief_complaint_concept_ids = page_config["PATIENT COMPLAINT"][
            "Chief Complaint"
        ]

        visit_occurrence = self.visit_occurrence_repository.get_visit_occurrence(
            case_id
        )

        person = self.person_repository.get_person(visit_occurrence.person_id)
        age = get_age(person, visit_occurrence)
        gender = self.get_concept_name(person.gender_concept_id)
        observations = self.observation_repository.get_observations_by_type(
            case_id, chief_complaint_concept_ids
        )
        patient_chief_complaint = []
        for obs in observations:
            concept_name = self.get_concept_name(obs.observation_concept_id)
            if concept_name and concept_name not in patient_chief_complaint:
                patient_chief_complaint.append(concept_name)

        case_summary = CaseSummary(
            config_id=config_id,
            case_id=case_id,
            age=age,
            gender=gender,
            patient_chief_complaint=", ".join(patient_chief_complaint),
        )
        cases_summary_list.append(case_summary)

        return cases_summary_list
