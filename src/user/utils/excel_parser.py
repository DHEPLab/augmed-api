from io import BytesIO
from typing import List

from openpyxl import load_workbook
from openpyxl.utils.cell import range_boundaries

from src.common.exception.BusinessException import BusinessException
from src.user.model.configuration import Configuration


class ExcelConfigurationParser:
    def __init__(self, excel_stream: BytesIO):
        self.workbook = load_workbook(filename=excel_stream)
        self.sheet = self.workbook.active

    def parse(self) -> List[Configuration]:
        configurations = []
        headers = [cell.value for cell in self.sheet[1]]
        user_index = headers.index("User")
        case_index = headers.index("Case No.")

        current_config = None

        for row in self.sheet.iter_rows(min_row=2, max_row=self.sheet.max_row):
            row_data = [cell.value for cell in row]
            current_config = self._parse_row(
                row,
                row_data,
                headers,
                user_index,
                case_index,
                current_config,
                configurations,
            )

        return configurations

    def _parse_row(
            self,
            row,
            row_data,
            headers,
            user_index,
            case_index,
            current_config,
            configurations,
    ):
        data_dict = dict(zip(headers, row_data))

        user_cell = row[user_index]
        case_cell = row[case_index]

        user = self._resolve_merged_cells(user_cell)
        case = self._resolve_merged_cells(case_cell)

        if user is None:
            user = current_config.user_email if current_config else None
        if case is None:
            case = current_config.case_id if current_config else None

        if not user:
            print("Invalid user email in config file.")
            return current_config

        try:
            case_id = int(case)
        except (ValueError, TypeError):
            print("Invalid case id in config file.")
            return current_config

        if (
                current_config is None
                or current_config.user_email != user
                or current_config.case_id != case_id
        ):
            current_config = Configuration(
                user_email=user, case_id=case_id, path_config=[]
            )
            configurations.append(current_config)

        path = data_dict.get("Path")
        collapse = data_dict.get("Collapse")
        highlight = data_dict.get("Highlight")
        if path:
            style = self._build_style_dict(collapse, highlight)
            if style:
                current_config.path_config.append({"path": path, "style": style})

        return current_config

    def _get_or_create_config(self, user, case_id, current_config, configurations):
        if (
                current_config is None
                or current_config.user_email != user
                or current_config.case_id != case_id
        ):
            current_config = Configuration(
                user_email=user, case_id=case_id, path_config=[]
            )
            configurations.append(current_config)
        return current_config

    def _resolve_merged_cells(self, cell):
        if cell.value is not None:
            return cell.value
        for range_ in self.sheet.merged_cells.ranges:
            if cell.coordinate in range_:
                min_col, min_row, _, _ = range_boundaries(str(range_))
                return self.sheet.cell(row=min_row, column=min_col).value
        return None

    def _build_style_dict(self, collapse, highlight) -> dict:
        style = {}
        if collapse is not None:
            style["collapse"] = collapse
        if highlight is not None:
            style["highlight"] = highlight
        return style


def parse_excel_stream_to_configurations(excel_stream: BytesIO) -> List[Configuration]:
    parser = ExcelConfigurationParser(excel_stream)
    try:
        return parser.parse()
    except BusinessException as e:
        print(f"Error: {e}")
        return []
