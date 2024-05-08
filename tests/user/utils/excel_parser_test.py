from io import BytesIO

from openpyxl import Workbook

from src.user.utils.excel_parser import parse_excel_stream_to_configurations


def test_should_parse_excell_stream_correctly_when_all_config_are_set():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.abc', True, True])
    ws.merge_cells(start_row=2, start_column=1, end_row=3, end_column=1)
    ws.merge_cells(start_row=2, start_column=2, end_row=3, end_column=2)

    ws.append([None, None, 'background.xxx', True, False])
    ws.append(['userb@example.com', '1', 'Background.patient demo', False, False])
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)
    result_dicts = [config.to_dict() for config in result]

    # Define expected results
    expected_results = [
        {
            'user_email': 'usera@example.com',
            'case_id': 1,
            'path_config': [
                {'path': 'Background.abc', 'style': {'collapse': True, 'highlight': True}},
                {'path': 'background.xxx', 'style': {'collapse': True, 'highlight': False}}
            ]
        },
        {
            'user_email': 'userb@example.com',
            'case_id': 1,
            'path_config': [
                {'path': 'Background.patient demo', 'style': {'collapse': False, 'highlight': False}}
            ]
        }
    ]

    # Assert with a simple comparison
    assert result_dicts == expected_results


def test_should_ignore_none_config():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.abc', None, True])
    ws.append([None, None, 'background.xxx', True, None])
    ws.append([None, None, 'Background.patient demo', None, None])
    ws.merge_cells(start_row=2, start_column=1, end_row=4, end_column=1)
    ws.merge_cells(start_row=2, start_column=2, end_row=4, end_column=2)
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)

    # Check if the result matches the expected configuration
    assert len(result) == 1
    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 2

    # Assert the configuration of paths
    expected_path_0 = {
        'path': 'Background.abc',
        'style': {'highlight': True}
    }
    expected_path_1 = {
        'path': 'background.xxx',
        'style': {'collapse': True}
    }

    # Check each path configuration for correctness
    assert result[0].path_config[0] == expected_path_0
    assert result[0].path_config[1] == expected_path_1


def test_should_ignore_none_config_while_keep_user_case_relationship():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.patient demo', None, None])
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)
    assert len(result) == 1
    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 0


def test_should_ignore_blank_line():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.patient demo', None, None])
    ws.append([None, None, None, None, None])
    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)

    assert len(result) == 1
    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 0


def test_should_keep_duplicate_user_case_relationship():
    # Prepare the test data (Workbook with multiple configurations)
    wb = Workbook()
    ws = wb.active
    # Headers
    ws.append(['User', 'Case No.', 'Path', 'Collapse', 'Highlight'])
    # Data for multiple users and cases
    ws.append(['usera@example.com', '1', 'Background.patient demo', None, None])
    ws.append(['usera@example.com', '1', 'Background.patient demo', None, None])
    ws.append([None, None, 'Background.drug', None, None])
    ws.append(['usera@example.com', '1', None, None, None])

    excel_stream = BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    result = parse_excel_stream_to_configurations(excel_stream)

    assert len(result) == 3
    assert result[0].user_email == 'usera@example.com'
    assert result[0].case_id == 1
    assert len(result[0].path_config) == 0

    assert result[1].user_email == 'usera@example.com'

    assert result[1].case_id == 1
    assert len(result[1].path_config) == 0
    assert result[1].user_email == 'usera@example.com'

    assert result[2].case_id == 1
    assert len(result[1].path_config) == 0
    assert result[2].user_email == 'usera@example.com'
