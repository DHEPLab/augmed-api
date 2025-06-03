from collections import defaultdict
from operator import itemgetter

from src.answer.repository.answer_repository import AnswerRepository
from src.cases.controller.response.case_summary import CaseSummary
from src.cases.model.case import Case, TreeNode
from src.cases.repository.concept_repository import ConceptRepository
from src.cases.repository.drug_exposure_repository import DrugExposureRepository
from src.cases.repository.measurement_repository import MeasurementRepository
from src.cases.repository.observation_repository import ObservationRepository
from src.cases.repository.person_repository import PersonRepository
from src.cases.repository.visit_occurrence_repository import VisitOccurrenceRepository
from src.common.exception.BusinessException import (BusinessException, BusinessExceptionEnum)
from src.common.repository.system_config_repository import SystemConfigRepository
from src.user.repository.display_config_repository import DisplayConfigRepository
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
    return isinstance(config, list) or isinstance(config, int)


def get_age(person, visit_occurrence):
    return str(visit_occurrence.visit_start_date.year - person.year_of_birth)


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
        configuration_repository: DisplayConfigRepository,
        system_config_repository: SystemConfigRepository,
        diagnose_repository: AnswerRepository,
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
        """
        Build the full TreeNode hierarchy for this single case_id (== person_id).
        We do not prune anything here; we simply load every possible leaf.
        """
        page_config = self.get_page_configuration()
        title_resolvers = {
            "BACKGROUND": self.get_nodes_of_background,
            "PATIENT COMPLAINT": self.get_nodes_of_observation,
            "PHYSICAL EXAMINATION": self.get_nodes_of_measurement,
        }
        data: list[TreeNode] = []
        for key, title_config in page_config.items():
            # Each top‐level key (e.g. "BACKGROUND") becomes a TreeNode whose children we fill in next.
            candidate = TreeNode(key, title_resolvers[key](case_id, title_config))
            if candidate.values:
                data.append(candidate)
        return data

    def get_nodes_of_measurement(self, case_id, title_config):
        data: list[TreeNode] = []
        for key, title_concept_ids in title_config.items():
            section_name = self.get_concept_name(title_concept_ids[0])
            parent_measurements = self.measurement_repository.get_measurements(
                case_id, title_concept_ids
            )
            if parent_measurements:
                # Leaf‐level measurements (no further grouping needed)
                data.append(
                    TreeNode(
                        section_name,
                        get_value_of_rows(parent_measurements, self.get_value_of_measurement),
                    )
                )
            else:
                # Sometimes OMOP groups measurement_concept_id under parents; handle that.
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
                if parent_node.values:
                    data.append(parent_node)
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
            if parent_node.values:
                data.append(parent_node)
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
        """
        Build everything under “BACKGROUND.”  First add “Patient Demographics,” then
        one TreeNode per sub‐category (e.g. “Family History,” “Medical History,” etc.).
        Each sub‐category TreeNode's .values is a list of strings (all possible leaf texts).
        """
        data: list[TreeNode] = [
            self.get_nodes_of_patient(case_id),
        ]
        for key, config in title_config.items():
            node = TreeNode(key, self.get_nodes_of_nested_fields(case_id, config))
            if node.values:
                data.append(node)
        return data

    def get_nodes_of_patient(self, case_id):
        visit_occurrence = self.visit_occurrence_repository.get_visit_occurrence(case_id)
        person = self.person_repository.get_person(visit_occurrence.person_id)
        age = get_age(person, visit_occurrence)
        gender = self.get_concept_name(person.gender_concept_id)
        self.person = person
        # “Patient Demographics” is always a pair of leaves [“Age”, “Gender”]
        return TreeNode(
            "Patient Demographics",
            [TreeNode("Age", age), TreeNode("Gender", gender)],
        )

    def get_nodes_of_nested_fields(self, case_id, config):
        """
        Recursively build nested TreeNodes if config is a dict; if config is a list
        (i.e. a leaf concept_id list), fetch observations by those concept_ids.
        """
        if is_leaf_node(config):
            observations = self.observation_repository.get_observations_by_concept(
                case_id, config
            )
            return get_value_of_rows(observations, self.get_value_of_observation)
        data: list[TreeNode] = []
        for key, nested_config in config.items():
            node = TreeNode(key, self.get_nodes_of_nested_fields(case_id, nested_config))
            if node.values:
                data.append(node)
        return data

    def get_concept_name(self, concept_id):
        return self.concept_repository.get_concept(concept_id).concept_name

    def get_page_configuration(self):
        """
        The JSON config for “page_config” lives in `system_config`.
        Example (abbreviated):
        {
          "BACKGROUND": {
            "Family History": [4167217],
            "Social History": { "Smoke": [4041306], ... },
            "Medical History": [1008364],
            "CRC risk assessments": [45614722]
          },
          "PATIENT COMPLAINT": { "Chief Complaint": [38000282], ... },
          "PHYSICAL EXAMINATION": { "Abdominal": [4152368], ... }
        }
        """
        return self.system_config_repository.get_config_by_id("page_config").json_config

    def get_case_review(self, case_config_id):
        """
        1) Load the saved DisplayConfig (path_config list of { "path": "...", "style": {...} })
           for this case_config_id + user_email. If none or wrong user, error.
        2) Build the full “case_details” tree by calling `get_case_detail(case_id)`.
        3) Prune each parent (e.g. “Family History”, “Medical History”, etc.) down to exactly the
           leaves specified in path_config. Attach collapse/highlight/top style at the parent.
        4) If the raw CSV contained exactly the path "RISK ASSESSMENT.CRC risk assessments", then
           and only then fetch any “Adjusted CRC Risk: …” obs (concept_id = 45614722), rename it,
           and append as “AI Colorectal Cancer Risk Score” under importantInfos.
        5) Return a Case(...) object containing the pruned tree plus any “important info” nodes.
        """
        configuration = self.configuration_repository.get_configuration_by_id(case_config_id)
        current_user = get_user_email_from_jwt()
        if not configuration or configuration.user_email != current_user:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        # 1) Build the raw case_details (unpruned – contains all leaves)
        case_details = self.get_case_detail(configuration.case_id)

        # 2) Gather every single path_config entry into a map: parent_key → list of {leaf, style}
        raw_path_cfg = configuration.path_config or []
        parent_to_entries: dict[str, list[dict]] = defaultdict(list)

        # Also: detect if the CSV explicitly toggled CRC risk assessments at all
        has_crc_toggle = False

        for entry in raw_path_cfg:
            path_str = entry.get("path", "").strip()
            style_dict = entry.get("style", {}) or {}
            if not path_str:
                # skip lines with no path
                continue

            # If exactly "RISK ASSESSMENT.CRC risk assessments" appears, note it:
            if path_str == "RISK ASSESSMENT.CRC risk assessments":
                has_crc_toggle = True

            segments = path_str.split(".")
            if len(segments) < 2:
                # malformed, skip
                continue
            parent_key = ".".join(segments[:-1])  # e.g. "BACKGROUND.Family History"
            leaf_text = segments[-1]              # e.g. "Diabetes: Yes"
            parent_to_entries[parent_key].append({
                "leaf": leaf_text,
                "style": style_dict,
            })

        # 3) Build a list of important_infos for any node that has a “top” style
        important_infos: list[dict] = []

        # 4) Walk down case_details to prune each parent. We only prune under “BACKGROUND”
        for top_node in case_details:
            if top_node.key != "BACKGROUND":
                continue
            # top_node.values is a list of TreeNode children:
            #   [ TreeNode("Patient Demographics"), TreeNode("Family History"), TreeNode("Social History"),
            #     TreeNode("Medical History"), ... ]
            for child in top_node.values:
                # ALWAYS keep "Patient Demographics" as-is (Age/Gender). Skip pruning for it:
                if child.key == "Patient Demographics":
                    continue

                parent_key = f"BACKGROUND.{child.key}"
                if parent_key not in parent_to_entries:
                    # If CSV asked nothing about this parent, prune _all_ leaves under it.
                    child.values = []
                    continue

                # Otherwise, collect all leaf entries under this parent
                entries = parent_to_entries[parent_key]
                leaves_to_keep = {e["leaf"] for e in entries}

                # child.values was originally a list of strings (all possible leaves). Prune:
                child.values = [val for val in child.values if val in leaves_to_keep]

                # Merge all style dicts from entries for this parent into one combined style
                combined_style: dict = {}
                for e in entries:
                    style_dict = e.get("style") or {}
                    # CSV generator sets collapse=False to indicate “show this leaf” → invert it
                    if "collapse" in style_dict:
                        combined_style["collapse"] = not style_dict["collapse"]
                    if "highlight" in style_dict:
                        combined_style["highlight"] = style_dict["highlight"]
                    if "top" in style_dict:
                        # If multiple “top” values, pick the largest weight
                        if "top" not in combined_style or style_dict["top"] > combined_style["top"]:
                            combined_style["top"] = style_dict["top"]

                # Attach the merged style to this parent node
                child.style = combined_style

                # If there is a “top” key, add to important_infos
                if "top" in combined_style:
                    important_infos.append({
                        "key": child.key,
                        "values": child.values,
                        "weight": combined_style["top"],
                    })

        # 5) Sort important_infos by weight, then convert to TreeNode list
        important_infos.sort(key=itemgetter("weight"))
        sorted_important_infos = list(map(lambda e: TreeNode(e["key"], e["values"]), important_infos))

        # 6) ONLY if the CSV included "RISK ASSESSMENT.CRC risk assessments",
        #    fetch any “Adjusted CRC Risk: …” observation (concept_id = 45614722),
        #    rename it to “AI-Predicted CRC Risk Score”, and append as “AI Colorectal Cancer Risk Score”.
        if has_crc_toggle:
            crc_obs = self.observation_repository.get_observations_by_concept(
                configuration.case_id, [45614722]
            )
            for obs in crc_obs:
                if obs.value_as_string and obs.value_as_string.startswith("Adjusted CRC Risk"):
                    # Rewrite the leaf text: replace "Adjusted CRC Risk" with "AI-Predicted CRC Risk Score"
                    raw_text = obs.value_as_string  # e.g. "Adjusted CRC Risk: 0.546125"
                    new_leaf = raw_text.replace(
                        "Adjusted CRC Risk", "AI-Predicted CRC Risk Score"
                    )
                    # Use "AI Colorectal Cancer Risk Score" as the parent key
                    sorted_important_infos.append(
                        TreeNode("AI Colorectal Cancer Risk Score", [new_leaf])
                    )
                    break

        # 7) Return a Case object containing:
        #      • person_source_value (e.g. MRN or whatever)
        #      • case_id  (converted to str)
        #      • case_details
        #      • importantInfos  (only includes AI‐CRC node if CSV requested RISK ASSESSMENT toggles)
        return Case(
            self.person.person_source_value,
            str(configuration.case_id),
            case_details,
            sorted_important_infos,
        )

    def __get_current_case_by_user(self, user_email) -> tuple[int, str] | tuple[None, None]:
        case_config_pairs = (
            self.configuration_repository.get_case_configurations_by_user(user_email)
        )
        completed_case_list = self.diagnose_repository.get_answered_case_list_by_user(user_email)

        for case_id, config_id in case_config_pairs:
            if config_id not in completed_case_list:
                return case_id, config_id
        return None, None

    def get_cases_by_user(self, user_email) -> list[CaseSummary]:
        """
        Returns a list of CaseSummary for the _next_ incomplete case for this user.
        If none remain, returns [].
        """
        case_id, config_id = self.__get_current_case_by_user(user_email)
        if not case_id or not config_id:
            return []

        cases_summary_list: list[CaseSummary] = []
        page_config = self.get_page_configuration()
        chief_complaint_concept_ids = page_config["PATIENT COMPLAINT"]["Chief Complaint"]

        visit_occurrence = self.visit_occurrence_repository.get_visit_occurrence(case_id)
        person = self.person_repository.get_person(visit_occurrence.person_id)
        age = get_age(person, visit_occurrence)
        gender = self.get_concept_name(person.gender_concept_id)

        observations = self.observation_repository.get_observations_by_type(
            case_id, chief_complaint_concept_ids
        )
        patient_chief_complaint: list[str] = []
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
