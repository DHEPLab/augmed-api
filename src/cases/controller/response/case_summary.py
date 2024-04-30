from dataclasses import dataclass


@dataclass
class CaseSummary:
    config_id: int
    case_id: int
    patient_chief_complaint: str
    age: str
    gender: str
