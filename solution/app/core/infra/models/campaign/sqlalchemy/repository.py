import uuid

import dishka
import sqlalchemy.ext.asyncio

from app.core.domain.campaign.entities.entities import Campaign as DomainCampaign
from app.core.domain.campaign.entities.entities import Targeting as DomainTargeting
from app.core.domain.campaign.entities.repositories import CampaignRepository
from app.core.domain.client.entities.entities import Gender as DomainGender
from app.core.infra.models.campaign.sqlalchemy.campaign import Campaign, CampaignGender


class SQLAlchemyCampaignRepository(CampaignRepository):
    def __init__(
        self,
        session_factory: sqlalchemy.ext.asyncio.async_sessionmaker[
            sqlalchemy.ext.asyncio.AsyncSession
        ],
    ) -> None:
        self._session_factory = session_factory

    async def create_campaign(
        self,
        campaign: DomainCampaign,
        *,
        overwrite: bool = False,
    ) -> DomainCampaign:
        async with self._session_factory() as session, session.begin():
            new_campaign = Campaign(
                impressions_limit=campaign.impressions_limit,
                clicks_limit=campaign.clicks_limit,
                cost_per_impression=campaign.cost_per_impression,
                cost_per_click=campaign.cost_per_click,
                ad_title=campaign.ad_title,
                ad_text=campaign.ad_text,
                image_url=campaign.image_url,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                advertiser_id=campaign.advertiser_id,
            )

            if campaign.targeting:
                new_campaign.gender = campaign.targeting.gender
                new_campaign.age_from = campaign.targeting.age_from
                new_campaign.age_to = campaign.targeting.age_to
                new_campaign.location = campaign.targeting.location

            if campaign.id is not None:
                new_campaign.id = campaign.id

            if overwrite:
                new_campaign = await session.merge(new_campaign)

            session.add(new_campaign)

            await session.flush()
            session.expunge_all()

            targeting_options = {
                'gender': new_campaign.gender,
                'age_from': new_campaign.age_from,
                'age_to': new_campaign.age_to,
                'location': new_campaign.location,
            }

            return DomainCampaign(
                id=new_campaign.id,
                impressions_limit=new_campaign.impressions_limit,
                clicks_limit=new_campaign.clicks_limit,
                cost_per_impression=new_campaign.cost_per_impression,
                cost_per_click=new_campaign.cost_per_click,
                ad_title=new_campaign.ad_title,
                ad_text=new_campaign.ad_text,
                image_url=new_campaign.image_url,
                start_date=new_campaign.start_date,
                end_date=new_campaign.end_date,
                advertiser_id=new_campaign.advertiser_id,
                targeting=DomainTargeting(
                    **targeting_options,
                )
                if any(list(targeting_options.values()))
                else None,
            )

    async def get_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> DomainCampaign | None:
        async with self._session_factory() as session, session.begin():
            stmt = sqlalchemy.select(Campaign).where(Campaign.id == campaign_id)
            result = await session.execute(stmt)

            campaign = result.scalars().first()

            if campaign is None:
                return None

            targeting_options = {
                'gender': campaign.gender,
                'age_from': campaign.age_from,
                'age_to': campaign.age_to,
                'location': campaign.location,
            }

            return DomainCampaign(
                id=campaign.id,
                impressions_limit=campaign.impressions_limit,
                clicks_limit=campaign.clicks_limit,
                cost_per_impression=campaign.cost_per_impression,
                cost_per_click=campaign.cost_per_click,
                ad_title=campaign.ad_title,
                ad_text=campaign.ad_text,
                image_url=campaign.image_url,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                advertiser_id=campaign.advertiser_id,
                targeting=DomainTargeting(
                    **targeting_options,
                )
                if any(list(targeting_options.values()))
                else None,
            )

    async def delete_campaign(
        self,
        campaign_id: uuid.UUID,
        advertiser_id: uuid.UUID,
    ) -> None:
        async with self._session_factory() as session, session.begin():
            stmt = sqlalchemy.select(Campaign).where(
                Campaign.id == campaign_id,
                Campaign.advertiser_id == advertiser_id,
            )
            result = await session.execute(stmt)

            campaign = result.scalars().first()

            if campaign:
                await session.delete(campaign)
                await session.flush()

    async def get_advertiser_campaigns(
        self,
        advertiser_id: uuid.UUID,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[DomainCampaign]:
        async with self._session_factory() as session, session.begin():
            stmt = (
                sqlalchemy.select(Campaign)
                .where(Campaign.advertiser_id == advertiser_id)
                .offset(offset)
                .limit(limit)
            )

            result = await session.execute(stmt)
            campaigns = result.scalars().all()

            output = []

            for campaign in campaigns:
                targeting_options = {
                    'gender': campaign.gender,
                    'age_from': campaign.age_from,
                    'age_to': campaign.age_to,
                    'location': campaign.location,
                }

                output.append(
                    DomainCampaign(
                        id=campaign.id,
                        impressions_limit=campaign.impressions_limit,
                        clicks_limit=campaign.clicks_limit,
                        cost_per_impression=campaign.cost_per_impression,
                        cost_per_click=campaign.cost_per_click,
                        ad_title=campaign.ad_title,
                        ad_text=campaign.ad_text,
                        image_url=campaign.image_url,
                        start_date=campaign.start_date,
                        end_date=campaign.end_date,
                        advertiser_id=campaign.advertiser_id,
                        targeting=DomainTargeting(
                            **targeting_options,
                        )
                        if any(list(targeting_options.values()))
                        else None,
                    ),
                )

        return output

    async def get_targeted_campaigns(
        self,
        age: int,
        location: str,
        gender: DomainGender,
    ) -> list[DomainCampaign]:
        async with self._session_factory() as session, session.begin():
            stmt = sqlalchemy.select(Campaign)
            result = await session.execute(stmt)
            campaigns = result.scalars().all()

            session.expunge_all()

            output = []

            for campaign in campaigns:
                if campaign.age_from is not None and age < campaign.age_from:
                    continue

                if campaign.age_to is not None and age > campaign.age_to:
                    continue

                if (
                    campaign.gender is not None
                    and campaign.gender != CampaignGender.ALL
                    and campaign.gender != CampaignGender(gender)
                ):
                    continue

                if campaign.location is not None and campaign.location != location:
                    continue

                targeting_options = {
                    'gender': campaign.gender,
                    'age_from': campaign.age_from,
                    'age_to': campaign.age_to,
                    'location': campaign.location,
                }

                output.append(
                    DomainCampaign(
                        id=campaign.id,
                        impressions_limit=campaign.impressions_limit,
                        clicks_limit=campaign.clicks_limit,
                        cost_per_impression=campaign.cost_per_impression,
                        cost_per_click=campaign.cost_per_click,
                        ad_title=campaign.ad_title,
                        ad_text=campaign.ad_text,
                        image_url=campaign.image_url,
                        start_date=campaign.start_date,
                        end_date=campaign.end_date,
                        advertiser_id=campaign.advertiser_id,
                        targeting=DomainTargeting(
                            **targeting_options,
                        )
                        if any(list(targeting_options.values()))
                        else None,
                    ),
                )

        return output


repository_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
repository_provider.provide(SQLAlchemyCampaignRepository, provides=CampaignRepository)
