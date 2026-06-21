from app.repositories.lead_repository import LeadRepository
from app.schemas.lead import MetricsResponse


class MetricsService:
    def __init__(self, repository: LeadRepository) -> None:
        self.repository = repository

    async def get_metrics(self) -> MetricsResponse:
        return MetricsResponse(
            total=await self.repository.count_total(),
            by_category=await self.repository.count_by_category(),
            by_source=await self.repository.count_by_source(),
        )
