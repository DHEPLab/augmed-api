import json

from src.cases.controller.response.case_summary import CaseSummary
from src.common.model.system_config import SystemConfig
from src.user.model.configuration import Configuration
from tests.cases.case_fixture import input_case


def test_get_case_review(client, session, mocker):
    input_case(session)
    config = Configuration(
        user_email='goodbye@sunwukong.com',
        case_id=1,
        id='1',
    )
    session.add(
        config
    )
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
    mocker.patch('src.user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)
    mocker.patch('src.cases.service.case_service.get_user_email_from_jwt', return_value='goodbye@sunwukong.com')
    config_id = config.id
    response = client.get(f"/api/case-reviews/{config_id}")

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert json.dumps(data) == expected_json()


def expected_json():
    return '{"caseNumber": "1", "details": [{"key": "BACKGROUND", "style": null, "values": [{"key": "Patient Demographics", "style": null, "values": [{"key": "Age", "style": null, "values": "36"}, {"key": "Gender", "style": null, "values": "M"}]}, {"key": "Family History", "style": null, "values": ["family history", "10", "value", "10 per day", "qualifier : 10"]}, {"key": "Social History", "style": null, "values": [{"key": "Smoke", "style": null, "values": "nosmoke"}]}]}, {"key": "PATIENT COMPLAINT", "style": null, "values": [{"key": "Chief Complaint", "style": null, "values": [{"key": "Nested of Chief complaint", "style": null, "values": "duration"}]}, {"key": "Current Symptoms", "style": null, "values": [{"key": "1 of Current symptoms", "style": null, "values": "duration"}, {"key": "2 of Current symptoms", "style": null, "values": "duration"}]}]}, {"key": "PHYSICAL EXAMINATION", "style": null, "values": [{"key": "Vital signs", "style": null, "values": [{"key": "Pulse rate", "style": null, "values": "operator 10 unit"}, {"key": "BP", "style": null, "values": "operator value unit"}]}, {"key": "Abdominal", "style": null, "values": "10"}]}], "personName": "sunwukong"}'


def test_get_case_summary(client, mocker, session):
    mocker.patch('src.user.utils.auth_utils.validate_jwt_and_refresh', return_value=None)
    mocker.patch('src.user.utils.auth_utils.get_user_email_from_jwt', return_value='user@example.com')

    mocker.patch(
        "src.cases.service.case_service.CaseService.get_cases_by_user",
        return_value=[
            CaseSummary(
                config_id='1',
                case_id=1,
                patient_chief_complaint='Headache',
                age='36',
                gender='Male'
            ),
            CaseSummary(
                config_id='2',
                case_id=2,
                patient_chief_complaint='Cough',
                age='30',
                gender='Female'
            )
        ]
    )

    response = client.get("/api/cases")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    data = json.loads(response.data.decode())

    expected_data = {
        "error": None,
        "data": [
            {
                "config_id": '1',
                "case_id": 1,
                "patient_chief_complaint": "Headache",
                "age": "36",
                "gender": "Male"
            },
            {
                "config_id": '2',
                "case_id": 2,
                "patient_chief_complaint": "Cough",
                "age": "30",
                "gender": "Female"
            }
        ]
    }

    assert data == expected_data
