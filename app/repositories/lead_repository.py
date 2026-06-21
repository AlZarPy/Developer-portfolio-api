from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Lead, LeadCategory, LeadSentiment, LeadSource


class LeadRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        name: str,
        email: str,
        phone: str | None,
        message: str,
        source: LeadSource,
        category: LeadCategory,
        sentiment: LeadSentiment,
        ai_reply: str,
        email_sent: bool,
    ) -> Lead:
        lead = Lead(
            name=name,
            email=email,
            phone=phone,
            message=message,
            source=source,
            category=category,
            sentiment=sentiment,
            ai_reply=ai_reply,
            email_sent=email_sent,
        )
        self.session.add(lead)
        await self.session.commit()
        await self.session.refresh(lead)
        return lead

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count(Lead.id)))
        return int(result.scalar_one())

    async def count_by_category(self) -> dict[str, int]:
        statement: Select[tuple[LeadCategory, int]] = (
            select(Lead.category, func.count(Lead.id))
            .group_by(Lead.category)
            .order_by(Lead.category)
        )
        result = await self.session.execute(statement)
        return {category.value: count for category, count in result.all()}

    async def count_by_source(self) -> dict[str, int]:
        statement: Select[tuple[LeadSource, int]] = (
            select(Lead.source, func.count(Lead.id)).group_by(Lead.source).order_by(Lead.source)
        )
        result = await self.session.execute(statement)
        return {source.value: count for source, count in result.all()}
