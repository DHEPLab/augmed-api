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
from src.common.exception.BusinessException import (
    BusinessException,
    BusinessExceptionEnum,
)
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
                    if node.style.get("top") is not None:
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
                        get_value_of_rows(
                            parent_measurements, self.get_value_of_measurement
                        ),
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
        
        # Special handling for BMI (concept_id 40490382) - convert numeric to category
        if measurement.measurement_concept_id == 40490382 and measurement.value_as_number:
            bmi_num = int(measurement.value_as_number)
            bmi_categories = {
                18: "Underweight",
                22: "Normal",
                27: "Overweight",
                30: "Obese"
            }
            value = bmi_categories.get(bmi_num, str(bmi_num))
        elif measurement.value_as_number:
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
        visit_occurrence = self.visit_occurrence_repository.get_visit_occurrence(
            case_id
        )
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
            node = TreeNode(
                key, self.get_nodes_of_nested_fields(case_id, nested_config)
            )
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

    def get_case_review(self, case_config_id):  # pragma: no cover
        """
        1) Load DisplayConfig, verify access.
        2) Build full unpruned case_details tree.
        3) Prune under “BACKGROUND” per path_config.
        4) Handle CSV-provided literal Colorectal Cancer Score leaves (now possibly multiple):
           • collect all, compute min/max.
        5) Else if old CRC toggle, fetch from DB as before.
        6) Return Case with sorted important_infos.
        """
        # --- 1) Load configuration & verify access ---
        configuration = self.configuration_repository.get_configuration_by_id(
            case_config_id
        )
        current_user = get_user_email_from_jwt()
        if not configuration or configuration.user_email != current_user:
            raise BusinessException(BusinessExceptionEnum.NoAccessToCaseReview)

        # --- 2) Raw, unpruned case tree ---
        case_details = self.get_case_detail(configuration.case_id)

        # --- 3) Index CSV path_config entries ---
        raw_path_cfg = configuration.path_config or []
        parent_to_entries: dict[str, list[dict]] = defaultdict(list)

        # Track CSV-provided literal score overrides (now possibly many)
        csv_crc_score_leaves: list[str] = []
        old_crc_toggle = False

        for entry in raw_path_cfg:
            path_str = (entry.get("path") or "").strip()
            style = entry.get("style") or {}
            if not path_str:
                continue

            segments = path_str.split(".")
            if len(segments) < 2:
                continue

            parent_key = ".".join(segments[:-1])
            leaf_text = segments[-1]

            # collect any literal "Colorectal Cancer Score: X"
            if path_str.startswith("RISK ASSESSMENT.Colorectal Cancer Score"):
                csv_crc_score_leaves.append(leaf_text)

            # old-style toggle of entire CRC section
            if path_str == "RISK ASSESSMENT.CRC risk assessments":
                old_crc_toggle = True

            parent_to_entries[parent_key].append({"leaf": leaf_text, "style": style})

        # --- 4) Prune under BACKGROUND per path_config ---
        important_infos: list[dict] = []
        for top in case_details:
            if top.key != "BACKGROUND":
                continue
            for child in top.values:
                if child.key == "Patient Demographics":
                    continue  # always keep
                pk = f"BACKGROUND.{child.key}"
                if pk not in parent_to_entries:
                    child.values = []
                    continue
                entries = parent_to_entries[pk]
                keep = {e["leaf"] for e in entries}
                child.values = [v for v in child.values if v in keep]

                # merge style directives
                merged: dict = {}
                for e in entries:
                    s = e["style"]
                    if "collapse" in s:
                        merged["collapse"] = not s["collapse"]
                    if "highlight" in s:
                        merged["highlight"] = s["highlight"]
                    if "top" in s:
                        merged["top"] = max(merged.get("top", -1), s["top"])

                child.style = merged
                if merged.get("top") is not None:
                    important_infos.append(
                        {
                            "key": child.key,
                            "values": child.values,
                            "weight": merged["top"],
                        }
                    )
        
        # --- 4b) Prune PHYSICAL EXAMINATION per path_config ---
        for top in case_details:
            if top.key != "PHYSICAL EXAMINATION":
                continue
            for child in top.values:
                pk = f"PHYSICAL EXAMINATION.{child.key}"
                if pk not in parent_to_entries:
                    # If this section is not in path_config, remove all values
                    child.values = []
                    continue
                
                entries = parent_to_entries[pk]
                keep = {e["leaf"] for e in entries}
                
                # Filter child.values - handle both string lists and TreeNode lists
                if child.values and isinstance(child.values[0], TreeNode):
                    # child.values is a list of TreeNode objects
                    child.values = [v for v in child.values if v.key in keep]
                else:
                    # child.values is a list of strings
                    child.values = [v for v in child.values if v in keep]
                
                # Merge style directives
                merged: dict = {}
                for e in entries:
                    s = e["style"]
                    if "collapse" in s:
                        merged["collapse"] = not s["collapse"]
                    if "highlight" in s:
                        merged["highlight"] = s["highlight"]
                    if "top" in s:
                        merged["top"] = max(merged.get("top", -1), s["top"])
                
                child.style = merged
                if merged.get("top") is not None:
                    important_infos.append(
                        {
                            "key": child.key,
                            "values": child.values,
                            "weight": merged["top"],
                        }
                    )
        
        # --- 4c) Rename BMI title from 'centile' to 'range' after filtering ---
        for top in case_details:
            if top.key != "PHYSICAL EXAMINATION":
                continue
            for child in top.values:
                if child.key == "Body measure" and child.values:
                    if isinstance(child.values[0], TreeNode):
                        for node in child.values:
                            if node.key == "BMI (body mass index) centile":
                                node.key = "BMI (body mass index) range"

        # sort and wrap into TreeNodes
        important_infos.sort(key=itemgetter("weight"))
        sorted_important = [TreeNode(e["key"], e["values"]) for e in important_infos]

        # --- 5) Handle AI CRC Risk Score section ---
        ai_label = "AI CRC Risk Score (<6: Low; 6-11: Medium; >11: High)"

        if csv_crc_score_leaves:
            # parse all numeric scores
            nums = []
            for leaf in csv_crc_score_leaves:
                parts = leaf.split(":")
                if len(parts) == 2:
                    try:
                        nums.append(float(parts[1].strip()))
                    except ValueError:
                        pass

            # pick the "predicted" one (e.g. first)
            predicted_leaf = csv_crc_score_leaves[0]
            display_pred = predicted_leaf.replace(
                "Colorectal Cancer Score", "Predicted Colorectal Cancer Score"
            )
            sorted_important.append(TreeNode(ai_label, [display_pred]))

            # if we have numeric values, emit min/max
            if nums:
                min_val = int(min(nums))
                max_val = int(max(nums))
                sorted_important.append(
                    TreeNode("Min Predicted Colorectal Cancer Score", [str(min_val)])
                )
                sorted_important.append(
                    TreeNode("Max Predicted Colorectal Cancer Score", [str(max_val)])
                )

        elif old_crc_toggle:
            crc_obs = self.observation_repository.get_observations_by_concept(
                configuration.case_id, [45614722]
            )
            # (a) any literal "Colorectal Cancer Score: X"
            csv_obs = next(
                (
                    o.value_as_string
                    for o in crc_obs
                    if o.value_as_string
                    and o.value_as_string.startswith("Colorectal Cancer Score")
                ),
                None,
            )
            if csv_obs:
                display_txt = csv_obs.replace(
                    "Colorectal Cancer Score", "Predicted Colorectal Cancer Score"
                )
                sorted_important.append(TreeNode(ai_label, [display_txt]))
            else:
                # (b) fallback to Adjusted CRC Risk
                for obs in crc_obs:
                    txt = obs.value_as_string or ""
                    if txt.startswith("Adjusted CRC Risk"):
                        new_txt = txt.replace(
                            "Adjusted CRC Risk", "AI-Predicted CRC Risk Score"
                        )
                        sorted_important.append(TreeNode(ai_label, [new_txt]))
                        break
                else:
                    sorted_important.append(TreeNode(ai_label, ["N/A"]))

        # 6) done—return full Case
        return Case(
            self.person.person_source_value,
            str(configuration.case_id),
            case_details,
            sorted_important,
        )

    def __get_current_case_by_user(
        self, user_email
    ) -> tuple[int, str] | tuple[None, None]:
        case_config_pairs = (
            self.configuration_repository.get_case_configurations_by_user(user_email)
        )
        completed_case_list = self.diagnose_repository.get_answered_case_list_by_user(
            user_email
        )

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
