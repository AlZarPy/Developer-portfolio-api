from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_contact_service
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.schemas.lead import ContactRequest, PublicContactResponse
from app.services.contact_service import ContactService

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post(
    "",
    response_model=PublicContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a contact request",
)
@limiter.limit(get_settings().contact_rate_limit)
async def create_contact(
    request: Request,
    payload: ContactRequest,
    service: ContactService = Depends(get_contact_service),
) -> PublicContactResponse:
    return await service.process(payload)
