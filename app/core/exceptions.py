from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorCode:
    code: str
    message: str


VALIDATION_ERROR = ErrorCode("validation_error", "Request validation failed.")
INTERNAL_ERROR = ErrorCode("internal_error", "Unexpected server error.")
CONTACT_PROCESSING_ERROR = ErrorCode(
    "contact_processing_error",
    "Could not process the contact request.",
)
