from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class ValidationResult:
    validation_result_id: str
    run_id: str
    candidate_ref: str
    rule_code: str
    severity: str
    result: str
    message: str
