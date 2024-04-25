import json

from tests.cases.case_fixture import input_case


def test_get_case_review(client, mocker, session):
    input_case(session)

    mocker.patch(
        "src.cases.service.case_service.CONCEPT_IDS",
        {
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

    response = client.get("/api/cases/1")

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert json.dumps(data) == expected_json()


def expected_json():
    return '[{"key": "BACKGROUND", "style": null, "values": [{"key": "Patient Demographics", "style": null, "values": [{"key": "Age", "style": null, "values": "36"}, {"key": "Gender", "style": null, "values": "M"}]}, {"key": "Family History", "style": null, "values": ["family history", "10", "value", "10 per day", "qualifier : 10"]}, {"key": "Social History", "style": null, "values": [{"key": "Smoke", "style": null, "values": "nosmoke"}]}]}, {"key": "PATIENT COMPLAINT", "style": null, "values": [{"key": "Chief Complaint", "style": null, "values": [{"key": "Nested of Chief complaint", "style": null, "values": "duration"}]}, {"key": "Current Symptoms", "style": null, "values": [{"key": "1 of Current symptoms", "style": null, "values": "duration"}, {"key": "2 of Current symptoms", "style": null, "values": "duration"}]}]}, {"key": "PHYSICAL EXAMINATION", "style": null, "values": [{"key": "Vital signs", "style": null, "values": [{"key": "Pulse rate", "style": null, "values": "operator 10 unit"}, {"key": "BP", "style": null, "values": "operator value unit"}]}, {"key": "Abdominal", "style": null, "values": "10"}]}]'
