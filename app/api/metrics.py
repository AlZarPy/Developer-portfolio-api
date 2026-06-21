from fastapi import APIRouter, Depends

from app.api.dependencies import get_metrics_service
from app.schemas.lead import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("", response_model=MetricsResponse, summary="Get contact request metrics")
async def get_metrics(
    service: MetricsService = Depends(get_metrics_service),
) -> MetricsResponse:
    return await service.get_metrics()
