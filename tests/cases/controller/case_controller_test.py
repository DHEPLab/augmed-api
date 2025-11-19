import json

from src.cases.controller.response.case_summary import CaseSummary
from src.common.model.system_config import SystemConfig
from src.user.model.display_config import DisplayConfig
from tests.cases.case_fixture import input_case


def test_get_case_review(client, session, mocker):
    input_case(session)

    config = DisplayConfig(user_email="goodbye@sunwukong.com", case_id=1, id="1")
    session.add(config)

    session.add(
        SystemConfig(
            id="page_config",
            json_config={
                "BACKGROUND": {
                    "Family History": [4167217],
                    "Social History": {
                        "Smoke": [4041306],
                        "Alcohol": [4238768],
                        "Drug use": [4038710],
                        "Sexual behavior": [4283657, 4314454],
                    },
                },
                "PATIENT COMPLAINT": {
                    "Chief Complaint": [38000282],
                    "Current Symptoms": [4034855],
                },
                "PHYSICAL EXAMINATION": {
                    "Vital Signs": [4263222],
                    "Abdominal": [4152368],
                },
            },
        )
    )
    session.flush()

    mocker.patch(
        "src.user.utils.auth_utils.validate_jwt_and_refresh", return_value=None
    )
    mocker.patch(
        "src.cases.service.case_service.get_user_email_from_jwt",
        return_value="goodbye@sunwukong.com",
    )

    response = client.get(f"/api/case-reviews/{config.id}")

    assert response.status_code == 200
    data = response.get_json()["data"]

    # Convert golden file to the form produced by the service
    expected = expected_json()
    expected["details"][0]["values"][1]["values"] = []
    expected["details"][0]["values"][2]["values"] = []
    
    # PHYSICAL EXAMINATION is not filtered by path_config, so values remain as-is
    # (golden file already has the correct PHYSICAL EXAMINATION values)

    # when CSV doesn't reference any RISK ASSESSMENT, importantInfos should be empty
    expected["importantInfos"] = []

    assert data == expected


def test_get_case_review_with_physical_exam_filtering(client, session, mocker):
    """Test that PHYSICAL EXAMINATION items are filtered based on path_config"""
    input_case(session)

    # Config with PHYSICAL EXAMINATION items in path_config
    config = DisplayConfig(
        user_email="goodbye@sunwukong.com",
        case_id=1,
        id="2",
        path_config=[
            {"path": "BACKGROUND.Patient Demographics.Age"},
            {"path": "BACKGROUND.Patient Demographics.Gender"},
            {"path": "PHYSICAL EXAMINATION.Vital signs.Pulse rate"},  # Only keep Pulse rate
        ]
    )
    session.add(config)

    session.add(
        SystemConfig(
            id="page_config",
            json_config={
                "BACKGROUND": {
                    "Family History": [4167217],
                    "Social History": {
                        "Smoke": [4041306],
                        "Alcohol": [4238768],
                        "Drug use": [4038710],
                        "Sexual behavior": [4283657, 4314454],
                    },
                },
                "PATIENT COMPLAINT": {
                    "Chief Complaint": [38000282],
                    "Current Symptoms": [4034855],
                },
                "PHYSICAL EXAMINATION": {
                    "Vital Signs": [4263222],
                    "Abdominal": [4152368],
                },
            },
        )
    )
    session.flush()

    mocker.patch(
        "src.user.utils.auth_utils.validate_jwt_and_refresh", return_value=None
    )
    mocker.patch(
        "src.cases.service.case_service.get_user_email_from_jwt",
        return_value="goodbye@sunwukong.com",
    )

    response = client.get(f"/api/case-reviews/{config.id}")

    assert response.status_code == 200
    data = response.get_json()["data"]

    # Physical examination should only have "Pulse rate" since that's in path_config
    phys_exam = next((d for d in data["details"] if d["key"] == "PHYSICAL EXAMINATION"), None)
    assert phys_exam is not None
    
    # Should have Vital signs section
    vital_signs = next((v for v in phys_exam["values"] if v["key"] == "Vital signs"), None)
    assert vital_signs is not None
    
    # Vital signs should only have "Pulse rate"
    assert len(vital_signs["values"]) == 1
    assert vital_signs["values"][0]["key"] == "Pulse rate"


def expected_json():
    with open("tests/cases/controller/expected_response.json") as f:
        return json.load(f)


def test_get_case_summary(client, mocker, session):
    mocker.patch(
        "src.user.utils.auth_utils.validate_jwt_and_refresh", return_value=None
    )
    mocker.patch(
        "src.user.utils.auth_utils.get_user_email_from_jwt",
        return_value="user@example.com",
    )

    mocker.patch(
        "src.cases.service.case_service.CaseService.get_cases_by_user",
        return_value=[
            CaseSummary(
                config_id="1",
                case_id=1,
                patient_chief_complaint="Headache",
                age="36",
                gender="Male",
            ),
            CaseSummary(
                config_id="2",
                case_id=2,
                patient_chief_complaint="Cough",
                age="30",
                gender="Female",
            ),
        ],
    )

    response = client.get("/api/cases")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data.decode())

    expected_data = {
        "error": None,
        "data": [
            {
                "config_id": "1",
                "case_id": 1,
                "patient_chief_complaint": "Headache",
                "age": "36",
                "gender": "Male",
            },
            {
                "config_id": "2",
                "case_id": 2,
                "patient_chief_complaint": "Cough",
                "age": "30",
                "gender": "Female",
            },
        ],
    }

    assert data == expected_data
