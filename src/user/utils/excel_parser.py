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
        header = [
            cell
            for cell in next(
                self.sheet.iter_rows(min_row=1, max_row=1, values_only=True)
            )
        ]
        for row in self.sheet.iter_rows(min_row=2, values_only=True):

            if not any(row):
                continue  # Skip fully blank lines

            row_data = dict(zip(header, row))
            user = row_data.get("User")
            case = row_data.get("Case No.")
            path = row_data.get("Path")
            collapse = row_data.get("Collapse")
            highlight = row_data.get("Highlight")
            current_config = self._process_row(
                current_config, configurations, user, case, path, collapse, highlight
            )

        return configurations

    def _process_row(
        self, current_config, configurations, user, case, path, collapse, highlight
    ):
        if self._is_part_of_merged_cells(user, case, path):
            if current_config:
                self._add_path_config_to_last(current_config, path, collapse, highlight)
            return current_config

        else:
            # 否则，这是一个重复的行，添加到当前配置
            current_config = self._create_new_config(user, case)
            self._add_path_config_to_last(current_config, path, collapse, highlight)
            configurations.append(current_config)
            return current_config

    def _is_part_of_merged_cells(self, user, case, path):
        return user is None and case is None and path is not None

    def _create_new_config(self, user, case) -> Configuration:
        # 创建新的 Configuration 实例时，确保 user 和 case 不是 None
        user_email = user if user is not None else ""
        case_id = case if case is not None else 0
        return Configuration(
            user_email=user_email, case_id=int(case_id), path_config=[]
        )

    def _add_path_config_to_last(self, config, path, collapse, highlight):
        if path is not None and config:
            style = self._build_style_dict(collapse, highlight)
            if style:
                config.path_config.append({"path": path, "style": style})

    def _build_style_dict(self, collapse, highlight) -> dict:
        style = {}
        if collapse is not None:
            style["collapse"] = collapse
        if highlight is not None:
            style["highlight"] = highlight
        return style


def parse_excel_stream_to_configurations(excel_stream: BytesIO) -> List[Configuration]:
    parser = ExcelConfigurationParser(excel_stream)
    return parser.parse()
