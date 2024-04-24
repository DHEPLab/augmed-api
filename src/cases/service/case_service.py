from collections import defaultdict

from src.cases.model.case import TreeNode
from src.cases.repository.concept_repository import ConceptRepository
from src.cases.repository.drug_exposure_repository import \
    DrugExposureRepository
from src.cases.repository.measurement_repository import MeasurementRepository
from src.cases.repository.observation_repository import ObservationRepository
from src.cases.repository.person_repository import PersonRepository
from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.common.constants import CONCEPT_IDS


def get_page_configuration():
    return CONCEPT_IDS


def group_by(source_list, key_selector):
    target_list = defaultdict(list)
    for item in source_list:
        target_list[key_selector(item)].append(item)
    return target_list


def get_value_of_rows(rows, get_func):
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


class CaseService:
    def __init__(
        self,
        visit_occurrence_repository: VisitOccurrenceRepository,
        concept_repository: ConceptRepository,
        measurement_repository: MeasurementRepository,
        observation_repository: ObservationRepository,
        person_repository: PersonRepository,
        drug_exposure_repository: DrugExposureRepository,
    ):
        self.visit_occurrence_repository = visit_occurrence_repository
        self.concept_repository = concept_repository
        self.measurement_repository = measurement_repository
        self.observationRepository = observation_repository
        self.person_repository = person_repository
        self.drug_exposure_repository = drug_exposure_repository

    def get_case_detail(self, case_id: int):
        page_config = get_page_configuration()
        title_resolvers = {
            "BACKGROUND": self.get_nodes_of_background,
            "PATIENT COMPLAINT": self.get_nodes_of_observation,
            "PHYSICAL EXAMINATION": self.get_nodes_of_measurement,
        }
        data: list[TreeNode] = []
        # TODO into one line, no data no show
        for key, title_config in page_config.items():
            data.append(TreeNode(key, title_resolvers[key](case_id, title_config)))
        return data

    def get_nodes_of_measurement(self, case_id, title_config):
        data: list[TreeNode] = []
        for key, title_concept_ids in title_config.items():
            section_name = self.get_concept_name(title_concept_ids)
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
                data.append(parent_node)
        # TODO Lab&Diagnose
        return data

    def get_value_of_measurement(self, measurement) -> str | None:
        value = None
        if measurement.value_as_number:
            value = str(measurement.value_as_number)
        elif measurement.value_as_concept_id:
            value = self.get_concept_name(measurement.value_as_concept_id)
        if value and measurement.unit_concept_id:
            value = value + " " + self.get_concept_name(measurement.unit_concept_id)
        if value and measurement.operator_concept_id:
            value = self.get_concept_name(measurement.operator_concept_id) + " " + value
        return value

    def get_nodes_of_observation(self, case_id, title_config):
        data: list[TreeNode] = []
        for key, concept_type_ids in title_config.items():
            parent_node = TreeNode(key, [])
            observations = self.observationRepository.get_observations_by_type(
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
            data.append(parent_node)
            # TODO HPI hard code?
        return data

    def get_value_of_observation(self, observation) -> str | None:
        value = None
        if observation.value_as_string:
            value = observation.value_as_string
        elif observation.value_as_number:
            value = str(observation.value_as_number)
        elif observation.value_as_concept_id:
            value = self.get_concept_name(observation.value_as_concept_id)
        if value and observation.unit_concept_id:
            value = value + " " + self.get_concept_name(observation.unit_concept_id)
        if value and observation.qualifier_concept_id:
            value = (
                self.get_concept_name(observation.qualifier_concept_id) + " : " + value
            )
        return value

    def get_concept_name(self, *concept_ids):
        return self.concept_repository.get_concept(concept_ids[0]).concept_name

    def get_nodes_of_background(self, case_id, title_config):
        data: list[TreeNode] = [
            self.get_nodes_of_patient(case_id),
            self.get_nodes_of_drug(case_id),
        ]
        for key, config in title_config.items():
            data.append(TreeNode(key, self.get_nodes_of_nested_fields(case_id, config)))
        return data

    def get_nodes_of_patient(self, case_id):
        visit_occurrence = self.visit_occurrence_repository.get_visit_occurrence(
            case_id
        )
        person = self.person_repository.get_person(visit_occurrence.person_id)
        age = get_age(person, visit_occurrence)
        gender = self.get_concept_name(person.gender_concept_id)
        return TreeNode(
            "Patient Demographics", [TreeNode("Age", age), TreeNode("Gender", gender)]
        )

    def get_nodes_of_drug(self, case_id):
        drugs = self.drug_exposure_repository.get_drugs(case_id)
        drug_nodes = []
        for drug in drugs:
            drug_nodes.append(
                TreeNode(
                    self.get_concept_name(drug.drug_concept_id),
                    self.get_value_of_drug(drug),
                )
            )
        return TreeNode("Medical History", drug_nodes)

    def get_nodes_of_nested_fields(self, case_id, config):
        if is_leaf_node(config):
            observations = self.observationRepository.get_observations_by_concept(
                case_id, config
            )
            return get_value_of_rows(observations, self.get_value_of_observation)
        data: list[TreeNode] = []
        for key, nested_config in config.items():
            node = TreeNode(
                key, self.get_nodes_of_nested_fields(case_id, nested_config)
            )
            data.append(node)
        return data

    @staticmethod
    def get_value_of_drug(drug):
        return [
            "Quantity: {quantity}".format(quantity=str(drug.quantity)),
            "Duration: {duration}".format(duration=str(drug.days_supply)),
        ]
