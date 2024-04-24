from io import BytesIO
from typing import List

from openpyxl import load_workbook

from src.user.model.configuration import Configuration


class ExcelConfigurationParser:
    def __init__(self, excel_stream: BytesIO):
        self.workbook = load_workbook(filename=excel_stream)
        self.sheet = self.workbook.active

    def parse(self) -> List[Configuration]:
        configurations = []
        current_config = None
        header = [cell for cell in next(self.sheet.iter_rows(min_row=1, max_row=1, values_only=True))]
        print('header', header)
        for row in self.sheet.iter_rows(min_row=2, values_only=True):
            print('row', row)

            if not any(row):
                continue  # Skip fully blank lines

            row_data = dict(zip(header, row))
            user = row_data.get('User')
            case = row_data.get('Case No.')
            path = row_data.get('Path')
            collapse = row_data.get('Collapse')
            highlight = row_data.get('Highlight')
            current_config = self._process_row(
                current_config, configurations, user, case, path, collapse, highlight
            )

        return configurations

    def _process_row(
            self, current_config, configurations, user, case, path, collapse, highlight
    ):
        if self._is_part_of_merged_cells(user, case):
            self._add_path_config_to_last(current_config, path, collapse, highlight)
            return current_config

        return self._handle_new_or_existing_config(
            current_config, configurations, user, case, path, collapse, highlight
        )

    def _is_part_of_merged_cells(self, user, case):
        return user is None and case is None

    def _handle_new_or_existing_config(
            self, current_config, configurations, user, case, path, collapse, highlight
    ):
        if (
                current_config is None
                or user != current_config.user_email
                or case != current_config.case_id
        ):
            current_config = self._create_new_config(user, case)
            configurations.append(current_config)

        if path is not None:
            self._add_path_config(current_config, path, collapse, highlight)

        return current_config

    @staticmethod
    def _create_new_config(user, case) -> Configuration:
        return Configuration(user_email=user, case_id=int(case), path_config=[])

    def _add_path_config(self, config, path, collapse, highlight):
        style = self._build_style_dict(collapse, highlight)
        if style:
            config.path_config.append({"path": path, "style": style})

    def _add_path_config_to_last(self, config, path, collapse, highlight):
        if path is not None and config:
            style = self._build_style_dict(collapse, highlight)
            if style:
                config.path_config.append({"path": path, "style": style})

    @staticmethod
    def _build_style_dict(collapse, highlight) -> dict:
        style = {}
        if collapse is not None:
            style["Collapse"] = collapse
        if highlight is not None:
            style["Highlight"] = highlight
        return style


def parse_excel_stream_to_configurations(excel_stream: BytesIO) -> List[Configuration]:
    parser = ExcelConfigurationParser(excel_stream)
    return parser.parse()
