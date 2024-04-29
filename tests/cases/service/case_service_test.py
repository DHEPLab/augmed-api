from src.cases.model.case import TreeNode
from src.cases.repository.concept_repository import ConceptRepository
from src.cases.repository.drug_exposure_repository import \
    DrugExposureRepository
from src.cases.repository.measurement_repository import MeasurementRepository
from src.cases.repository.observation_repository import ObservationRepository
from src.cases.repository.person_repository import PersonRepository
from src.cases.repository.visit_occurrence_repository import \
    VisitOccurrenceRepository
from src.cases.service.case_service import (CaseService, add_if_value_present,
                                            attach_style, get_age,
                                            get_value_of_rows, group_by,
                                            is_leaf_node)
from src.user.model.configuration import Configuration
from src.user.repository.configuration_repository import \
    ConfigurationRepository
from tests.cases.case_fixture import (concept_fixture, measurement_fixture,
                                      observation_fixture, person_fixture,
                                      visit_occurrence_fixture)


class TestGroupBy:
    def test_group_by(self):
        source_list = [
            {"concept_id": 1, "value": "row1"},
            {"concept_id": 1, "value": "row2"},
            {"concept_id": 2, "value": "row"},
        ]

        target_list = group_by(source_list, lambda item: item["concept_id"])

        assert target_list[1] == [
            {"concept_id": 1, "value": "row1"},
            {"concept_id": 1, "value": "row2"},
        ]
        assert target_list[2] == [{"concept_id": 2, "value": "row"}]


class TestGetValueOfRows:
    def test_get_str_when_one_row(self):
        rows = [{"value": "text"}]

        value_of_rows = get_value_of_rows(rows, lambda item: item["value"])

        assert value_of_rows == "text"

    def test_get_list_str_when_many_rows(self):
        rows = [{"value": "text"}, {"value": "text"}]

        value_of_rows = get_value_of_rows(rows, lambda item: item["value"])

        assert value_of_rows == ["text", "text"]


class TestIsLeafNode:
    def test_is_leaf_when_config_is_list(self):
        config = [123]

        assert is_leaf_node(config) is True

    def test_is_leaf_when_config_is_a_number(self):
        config = 123

        assert is_leaf_node(config) is True


class TestGetAge:
    def test_get_age(self):
        person = person_fixture()
        visit = visit_occurrence_fixture()

        assert get_age(person, visit) == "36"


class TestAddIfPresent:
    def test_add_if_value_present(self):
        node_with_values = TreeNode("key", ["value"])
        node_without_values = TreeNode("key", None)

        data = []
        add_if_value_present(data, node_with_values)
        assert len(data) == 1

        data = []
        add_if_value_present(data, node_without_values)
        assert len(data) == 0


class TestAttachStyle:
    def test_attach_style_to_configuration_when_path_found_in_first_layer(self):
        case_details = [
            TreeNode(
                "levelOne", [TreeNode("levelTwo", [TreeNode("levelTree", "text")])]
            ),
            TreeNode("another", "xxx"),
        ]
        display_config = {"path": "levelOne", "style": "style"}

        attach_style(display_config, case_details)

        assert case_details[0].style == "style"

    def test_attach_style_to_configuration_when_path_found_in_nested_layer(self):
        case_details = [
            TreeNode(
                "levelOne", [TreeNode("levelTwo", [TreeNode("levelTree", "text")])]
            ),
            TreeNode("another", "xxx"),
        ]
        display_config = {"path": "levelOne.levelTwo.levelTree", "style": "style"}

        attach_style(display_config, case_details)

        assert case_details[0].values[0].values[0].style == "style"

    def test_not_attach_style_to_configuration_when_path_not_found(self):
        case_details = [
            TreeNode(
                "levelOne", [TreeNode("levelTwo", [TreeNode("levelTree", "text")])]
            ),
        ]
        display_config = {"path": "levelOne.levelTwo.xxx", "style": "style"}

        attach_style(display_config, case_details)

        assert case_details[0].style is None
        assert case_details[0].values[0].style is None
        assert case_details[0].values[0].values[0].style is None


def mock_repos(mocker):
    visit_occurrence_repository = mocker.Mock(VisitOccurrenceRepository)
    measurement_repository = mocker.Mock(MeasurementRepository)
    observation_repository = mocker.Mock(ObservationRepository)
    person_repository = mocker.Mock(PersonRepository)
    drug_exposure_repository = mocker.Mock(DrugExposureRepository)
    configuration_repository = mocker.Mock(ConfigurationRepository)
    concept_repository = mocker.Mock(ConceptRepository)

    visit_occurrence_repository.get_visit_occurrence.return_value = (
        visit_occurrence_fixture()
    )
    person_repository.get_person.return_value = person_fixture()
    concept_repository.get_concept.return_value = concept_fixture()
    observation_repository.get_observations_by_concept.return_value = []
    observation_repository.get_observations_by_type.return_value = []
    measurement_repository.get_measurements.return_value = []
    measurement_repository.get_measurements_of_parents.return_value = []
    return (
        concept_repository,
        configuration_repository,
        drug_exposure_repository,
        measurement_repository,
        observation_repository,
        person_repository,
        visit_occurrence_repository,
    )


def mock_concept_func(concept_id):
    mock_data = {
        4086988: "Physical Characteristics",
        4263222: "Vital Signs",
        36717771: "Cardiovascular",
        4080843: "Ophthalmology",
        4090320: "Abdominal",
        4152368: "Physical Characteristics",
        4154954: "Neurological",
    }
    if mock_data.get(concept_id):
        return concept_fixture(concept_id, mock_data[concept_id])
    return concept_fixture()


class TestGetCaseDetail:
    def test_get_patient_in_background(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        assert detail == [
            TreeNode(
                "BACKGROUND",
                [
                    TreeNode(
                        "Patient Demographics",
                        [TreeNode("Age", "36"), TreeNode("Gender", "test")],
                    )
                ],
            )
        ]

    def test_get_nested_fields_in_background(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        observation_repository.get_observations_by_concept.return_value = [
            observation_fixture(concept_id=1, value_as_string="value")
        ]

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        background = detail[0]
        assert background.values[1].key == "Family History"
        assert background.values[2].key == "Social History"
        assert background.values[2].values[0].key == "Smoke"
        assert background.values[2].values[1].key == "Alcohol"
        assert background.values[2].values[2].key == "Drug use"
        assert background.values[2].values[3].key == "Sexual behavior"

    def test_get_node_in_patient_complaint(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        observation_repository.get_observations_by_type.return_value = [
            observation_fixture(concept_id=1, value_as_string="value")
        ]

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        patient_complaint = detail[1]
        assert patient_complaint.key == "PATIENT COMPLAINT"
        assert patient_complaint.values[0].key == "Chief Complaint"
        assert patient_complaint.values[1].key == "Current Symptoms"

    def test_get_physical_examination_when_found_by_concept_itself(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        concept_repository.get_concept.side_effect = mock_concept_func
        measurement_repository.get_measurements.return_value = [
            measurement_fixture(concept_id=1, value_as_number=1)
        ]

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        physical_examination = detail[1]
        assert physical_examination.key == "PHYSICAL EXAMINATION"
        assert physical_examination.values[0].key == "Physical Characteristics"
        assert isinstance(physical_examination.values[0].values, str)
        assert physical_examination.values[1].key == "Vital Signs"
        assert isinstance(physical_examination.values[1].values, str)
        assert physical_examination.values[2].key == "Cardiovascular"
        assert isinstance(physical_examination.values[2].values, str)
        assert physical_examination.values[3].key == "Ophthalmology"
        assert isinstance(physical_examination.values[3].values, str)
        assert physical_examination.values[4].key == "Abdominal"
        assert isinstance(physical_examination.values[4].values, str)
        assert physical_examination.values[5].key == "Physical Characteristics"
        assert isinstance(physical_examination.values[5].values, str)
        assert physical_examination.values[6].key == "Neurological"
        assert isinstance(physical_examination.values[6].values, str)

    def test_get_physical_examination_when_found_by_concept_relationship(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        concept_repository.get_concept.side_effect = mock_concept_func
        measurement_repository.get_measurements_of_parents.return_value = [
            measurement_fixture(concept_id=1, value_as_number=1)
        ]

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )

        # When
        detail = case_service.get_case_detail(1)

        # Then
        physical_examination = detail[1]
        assert physical_examination.key == "PHYSICAL EXAMINATION"
        assert physical_examination.values[0].key == "Physical Characteristics"
        assert physical_examination.values[0].values == [TreeNode("test", "1")]
        assert physical_examination.values[1].key == "Vital Signs"
        assert physical_examination.values[1].values == [TreeNode("test", "1")]
        assert physical_examination.values[2].key == "Cardiovascular"
        assert physical_examination.values[2].values == [TreeNode("test", "1")]
        assert physical_examination.values[3].key == "Ophthalmology"
        assert physical_examination.values[3].values == [TreeNode("test", "1")]
        assert physical_examination.values[4].key == "Abdominal"
        assert physical_examination.values[4].values == [TreeNode("test", "1")]
        assert physical_examination.values[5].key == "Physical Characteristics"
        assert physical_examination.values[5].values == [TreeNode("test", "1")]
        assert physical_examination.values[6].key == "Neurological"
        assert physical_examination.values[6].values == [TreeNode("test", "1")]


class TestGetValue:
    def test_get_value_of_observation_with_string(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )
        observation_family_history_with_string = observation_fixture(
            concept_id=4167217,
            value_as_string="family history",
            observation_type_concept_id=0,
            observation_id=1,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_string
        )

        # then
        assert value == "family history"

    def test_get_value_of_observation_with_number(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )
        observation_family_history_with_number = observation_fixture(
            concept_id=4167217,
            value_as_number=10,
            observation_type_concept_id=0,
            observation_id=2,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_number
        )

        # then
        assert value == "10"

    def test_get_value_of_observation_with_concept(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )
        observation_family_history_with_concept = observation_fixture(
            concept_id=4167217,
            value_as_concept_id=31,
            observation_type_concept_id=0,
            observation_id=3,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_concept
        )

        # then
        assert value == "test"

    def test_get_value_of_observation_with_unit(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )
        observation_family_history_with_unit = observation_fixture(
            concept_id=4167217,
            value_as_number=10,
            unit_concept_id=32,
            observation_type_concept_id=0,
            observation_id=4,
            person_id=1,
            visit_id=1,
        )

        # When
        value = case_service.get_value_of_observation(
            observation_family_history_with_unit
        )

        # then
        assert value == "10 test"

    def test_get_value_of_observation_with_qualifier(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )
        observation_family_history_with_qualifier = observation_fixture(
            concept_id=4167217,
            value_as_number=10,
            qualifier_concept_id=33,
            observation_type_concept_id=0,
            observation_id=5,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_observation(
            observation_family_history_with_qualifier
        )

        # then
        assert value == "test : 10"

    def test_get_value_of_measurement_with_number(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )
        measurement_vital_signs_pulse_rate_with_number = measurement_fixture(
            concept_id=40,
            value_as_number=10,
            operator_concept_id=41,
            unit_concept_id=42,
            measurement_id=1,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_measurement(
            measurement_vital_signs_pulse_rate_with_number
        )

        # then
        assert value == "test 10 test"

    def test_get_value_of_measurement_with_concept(self, mocker):
        # Given
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)

        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )
        measurement_vital_signs_bp_with_concept = measurement_fixture(
            concept_id=43,
            value_as_concept_id=44,
            operator_concept_id=41,
            unit_concept_id=42,
            measurement_id=2,
            person_id=1,
            visit_id=1,
        )

        # when
        value = case_service.get_value_of_measurement(
            measurement_vital_signs_bp_with_concept
        )

        # then
        assert value == "test test test"


class TestGetCaseReview:
    def test_get_case_review_with_configuration_and_path_config(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)
        configuration_repository.get_configuration_by_id.return_value = Configuration(
            path_config=[
                {"path": "BACKGROUND.Patient Demographics", "style": {"collapse": True}},
                {"path": "no path", "style": {"collapse": True}},
            ]
        )
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )

        case_review = case_service.get_case_review(1, 1)

        assert case_review == [
            TreeNode(
                "BACKGROUND",
                [
                    TreeNode(
                        "Patient Demographics",
                        [TreeNode("Age", "36"), TreeNode("Gender", "test")],
                        {"collapse": True},
                    )
                ],
            )
        ]

    def test_get_case_review_without_configuration(self, mocker):
        (
            concept_repository,
            configuration_repository,
            drug_exposure_repository,
            measurement_repository,
            observation_repository,
            person_repository,
            visit_occurrence_repository,
        ) = mock_repos(mocker)
        configuration_repository.get_configuration_by_id.return_value = None
        case_service = CaseService(
            visit_occurrence_repository=visit_occurrence_repository,
            concept_repository=concept_repository,
            measurement_repository=measurement_repository,
            observation_repository=observation_repository,
            person_repository=person_repository,
            drug_exposure_repository=drug_exposure_repository,
            configuration_repository=configuration_repository,
        )

        case_review = case_service.get_case_review(1, 1)

        assert case_review == [
            TreeNode(
                "BACKGROUND",
                [
                    TreeNode(
                        "Patient Demographics",
                        [TreeNode("Age", "36"), TreeNode("Gender", "test")],
                    )
                ],
            )
        ]
