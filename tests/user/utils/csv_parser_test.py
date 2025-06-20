import csv
from io import StringIO

import pytest

from src.common.exception.BusinessException import BusinessException
from src.user.utils.csv_parser import parse_csv_stream_to_configurations, is_csv_file


def test_should_parse_csv_stream_correctly_when_all_config_are_set():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    # Headers
    writer.writerow(["User", "Case No.", "Path", "Collapse", "Highlight", "Top"])
    # Data for multiple users and cases
    writer.writerow(["usera@example.com", "1", "Background.abc", "TRUE", "True", 1])
    writer.writerow(["usera@example.com", "1", "background.xxx", "true", "False", 2])
    writer.writerow(
        ["userb@example.com", "1", "Background.patient demo", "FALSE", "false", 1.5]
    )
    stream.seek(0)

    result = parse_csv_stream_to_configurations(stream)
    result_dicts = [config.to_dict() for config in result]

    # Define expected results
    expected_results = [
        {
            "user_email": "usera@example.com",
            "case_id": 1,
            "path_config": [
                {
                    "path": "Background.abc",
                    "style": {"collapse": True, "highlight": True, "top": 1.0},
                },
                {
                    "path": "background.xxx",
                    "style": {"collapse": True, "highlight": False, "top": 2.0},
                },
            ],
        },
        {
            "user_email": "userb@example.com",
            "case_id": 1,
            "path_config": [
                {
                    "path": "Background.patient demo",
                    "style": {"collapse": False, "highlight": False, "top": 1.5},
                }
            ],
        },
    ]

    # Assert with a simple comparison
    assert result_dicts == expected_results


def test_should_ignore_none_config():
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(["User", "Case No.", "Path", "Collapse", "Highlight", "Top"])
    writer.writerow(["usera@example.com", "1", "Background.abc", None, True, None])
    writer.writerow(["usera@example.com", "1", "background.xxx", True, None, None])
    writer.writerow(
        ["usera@example.com", "1", "Background.patient demo", None, None, None]
    )
    stream.seek(0)

    result = parse_csv_stream_to_configurations(stream)

    assert len(result) == 1
    assert result[0].user_email == "usera@example.com"
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 3


def test_should_ignore_none_config_while_keep_user_case_relationship():
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(["User", "Case No.", "Path", "Collapse", "Highlight", "Top"])
    writer.writerow(
        ["usera@example.com", "1", "Background.patient demo", None, None, None]
    )
    stream.seek(0)

    result = parse_csv_stream_to_configurations(stream)

    assert len(result) == 1
    assert result[0].user_email == "usera@example.com"
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 1


def test_should_keep_duplicate_user_case_relationship():
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(["User", "Case No.", "Path", "Collapse", "Highlight", "Top"])
    writer.writerow(
        ["usera@example.com", "1", "Background.patient demo", None, None, None]
    )
    writer.writerow(["userb@example.com", "1", "Background.drug", None, None, None])
    writer.writerow(
        ["usera@example.com", "1", "Background.patient demo", None, None, None]
    )
    stream.seek(0)

    result = parse_csv_stream_to_configurations(stream)

    assert len(result) == 2


def test_invalid_user_email_raises_exception():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(["User", "Case No.", "Path", "Collapse", "Highlight", "Top"])
    writer.writerow(
        [None, "1", "Background.patient demo", None, None, None]
    )  # Invalid user
    stream.seek(0)

    with pytest.raises(BusinessException) as excinfo:
        parse_csv_stream_to_configurations(stream)

    assert "Invalid user email in config file." in str(excinfo.value.error.value)


def test_invalid_case_id_raises_exception():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(["User", "Case No.", "Path", "Collapse", "Highlight", "Top"])
    writer.writerow(
        ["usera@example.com", "abc", "Background.patient demo", None, None, None]
    )  # Invalid case ID
    stream.seek(0)

    with pytest.raises(BusinessException) as excinfo:
        parse_csv_stream_to_configurations(stream)

    assert "Invalid case id in config file." in str(excinfo.value.error.value)


def test_is_csv_file():
    csvs = ["test.csv"]
    not_csvs = ["test.numbers", "test.txt", "", None]

    for x in csvs:
        assert is_csv_file(x) is True
    for x in not_csvs:
        assert is_csv_file(x) is False


def test_invalid_non_number_top_config_should_raises_exception():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(["User", "Case No.", "Path", "Collapse", "Highlight", "Top"])
    writer.writerow(
        ["uset@test.com", "1", "Background.patient demo", None, None, "abc"]
    )
    stream.seek(0)

    with pytest.raises(BusinessException) as excinfo:
        parse_csv_stream_to_configurations(stream)

    assert "Error while processing csv file, please check again." in str(
        excinfo.value.error.value
    )


def test_invalid_top_config_on_root_node_should_raises_exception():
    # Prepare the test data
    stream = StringIO()
    writer = csv.writer(stream, delimiter=",")
    writer.writerow(["User", "Case No.", "Path", "Collapse", "Highlight", "Top"])
    writer.writerow(["uset@test.com", "1", "Background", None, None, 1])
    stream.seek(0)

    with pytest.raises(BusinessException) as excinfo:
        parse_csv_stream_to_configurations(stream)

    assert "Error while processing csv file, please check again." in str(
        excinfo.value.error.value
    )
