from dataclasses import dataclass


@dataclass
class CaseSummary:
    config_id: str
    case_id: int
    patient_chief_complaint: str
    age: str
    gender: str
