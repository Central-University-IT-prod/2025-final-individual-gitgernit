import asyncio
import uuid

import dishka

from app.core.domain.advertiser.entities.repositories import AdvertiserRepository
from app.core.domain.campaign.entities.entities import Campaign, Targeting
from app.core.domain.campaign.entities.repositories import CampaignRepository
from app.core.domain.campaign.service.dto import CampaignDTO, TargetingDTO
from app.core.domain.campaign.service.moderators import Moderator
from app.core.domain.campaign.service.text_generators import TextGenerator
from app.core.domain.options.entities.entities import AvailableOptions
from app.core.domain.options.entities.repositories import OptionsRepository


class AdvertiserNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__('No such advertiser found.')


class CampaignNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__('No such campaign found.')


class InvalidCampaignError(Exception):
    def __init__(self) -> None:
        super().__init__('Campaign was given invalid fields.')


class CampaignUsecase:
    def __init__(
        self,
        campaign_repository: CampaignRepository,
        advertiser_repository: AdvertiserRepository,
        options_repository: OptionsRepository,
        moderator: Moderator,
        text_generator: TextGenerator,
    ) -> None:
        self.campaign_repository = campaign_repository
        self.advertiser_repository = advertiser_repository
        self.options_repository = options_repository
        self.moderator = moderator
        self.text_generator = text_generator

    async def create_campaign(
        self,
        dto: CampaignDTO,
        *,
        overwrite: bool = False,
    ) -> CampaignDTO:
        if not await self.advertiser_repository.get_advertiser(dto.advertiser_id):
            raise AdvertiserNotFoundError

        campaign = Campaign(
            impressions_limit=dto.impressions_limit,
            clicks_limit=dto.clicks_limit,
            cost_per_impression=dto.cost_per_impression,
            cost_per_click=dto.cost_per_click,
            ad_title=dto.ad_title,
            ad_text=dto.ad_text,
            start_date=dto.start_date,
            end_date=dto.end_date,
            advertiser_id=dto.advertiser_id,
            targeting=Targeting(
                gender=dto.targeting.gender,
                age_from=dto.targeting.age_from,
                age_to=dto.targeting.age_to,
                location=dto.targeting.location,
            )
            if dto.targeting
            else None,
        )
        new_campaign = await self.campaign_repository.create_campaign(
            campaign,
            overwrite=overwrite,
        )

        asyncio.create_task(self.moderate_campaign(new_campaign.id))  # noqa

        return CampaignDTO(
            id=new_campaign.id,
            impressions_limit=new_campaign.impressions_limit,
            clicks_limit=new_campaign.clicks_limit,
            cost_per_impression=new_campaign.cost_per_impression,
            cost_per_click=new_campaign.cost_per_click,
            ad_title=new_campaign.ad_title,
            ad_text=new_campaign.ad_text,
            start_date=new_campaign.start_date,
            end_date=new_campaign.end_date,
            advertiser_id=new_campaign.advertiser_id,
            targeting=TargetingDTO(
                gender=new_campaign.targeting.gender,
                age_from=new_campaign.targeting.age_from,
                age_to=new_campaign.targeting.age_to,
                location=new_campaign.targeting.location,
            )
            if new_campaign.targeting
            else None,
        )

    async def get_campaign(
        self,
        campaign_id: uuid.UUID,
    ) -> CampaignDTO | None:
        campaign = await self.campaign_repository.get_campaign(
            campaign_id,
        )

        if campaign is None:
            return None

        return CampaignDTO(
            id=campaign.id,
            impressions_limit=campaign.impressions_limit,
            clicks_limit=campaign.clicks_limit,
            cost_per_impression=campaign.cost_per_impression,
            cost_per_click=campaign.cost_per_click,
            ad_title=campaign.ad_title,
            ad_text=campaign.ad_text,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            advertiser_id=campaign.advertiser_id,
            targeting=TargetingDTO(
                gender=campaign.targeting.gender,
                age_from=campaign.targeting.age_from,
                age_to=campaign.targeting.age_to,
                location=campaign.targeting.location,
            )
            if campaign.targeting
            else None,
        )

    async def patch_campaign(
        self,
        campaign_id: uuid.UUID,
        new_campaign_dto: CampaignDTO,
    ) -> CampaignDTO:
        if await self.campaign_repository.get_campaign(campaign_id) is None:
            raise CampaignNotFoundError

        campaign = Campaign(
            impressions_limit=new_campaign_dto.impressions_limit,
            clicks_limit=new_campaign_dto.clicks_limit,
            cost_per_impression=new_campaign_dto.cost_per_impression,
            cost_per_click=new_campaign_dto.cost_per_click,
            ad_title=new_campaign_dto.ad_title,
            ad_text=new_campaign_dto.ad_text,
            start_date=new_campaign_dto.start_date,
            end_date=new_campaign_dto.end_date,
            advertiser_id=new_campaign_dto.advertiser_id,
            targeting=Targeting(
                gender=new_campaign_dto.targeting.gender,
                age_from=new_campaign_dto.targeting.age_from,
                age_to=new_campaign_dto.targeting.age_to,
                location=new_campaign_dto.targeting.location,
            )
            if new_campaign_dto.targeting
            else None,
        )
        existing_campaign = await self.campaign_repository.get_campaign(
            campaign_id,
        )
        started = await existing_campaign.started(
            int((await self.options_repository.get_option(AvailableOptions.DAY)).value),
        )

        if (
            (
                campaign.impressions_limit != existing_campaign.impressions_limit
                and started
            )
            or (campaign.clicks_limit != existing_campaign.clicks_limit and started)
            or (campaign.start_date != existing_campaign.start_date and started)
            or (campaign.end_date != existing_campaign.end_date and started)
        ):
            raise InvalidCampaignError

        campaign_dict = campaign.model_dump(exclude={'id'})
        existing_campaign_dict = existing_campaign.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )

        new_campaign_dict = existing_campaign_dict | campaign_dict
        new_campaign = Campaign(**new_campaign_dict)

        new_campaign = await self.campaign_repository.create_campaign(
            new_campaign,
            overwrite=True,
        )

        asyncio.create_task(self.moderate_campaign(new_campaign.id))  # noqa

        return CampaignDTO(
            id=new_campaign.id,
            impressions_limit=new_campaign.impressions_limit,
            clicks_limit=new_campaign.clicks_limit,
            cost_per_impression=new_campaign.cost_per_impression,
            cost_per_click=new_campaign.cost_per_click,
            ad_title=new_campaign.ad_title,
            ad_text=new_campaign.ad_text,
            start_date=new_campaign.start_date,
            end_date=new_campaign.end_date,
            advertiser_id=new_campaign.advertiser_id,
            targeting=TargetingDTO(
                gender=new_campaign.targeting.gender,
                age_from=new_campaign.targeting.age_from,
                age_to=new_campaign.targeting.age_to,
                location=new_campaign.targeting.location,
            )
            if new_campaign.targeting
            else None,
        )

    async def delete_campaign(
        self,
        campaign_id: uuid.UUID,
        advertiser_id: uuid.UUID,
    ) -> None:
        if await self.campaign_repository.get_campaign(campaign_id) is None:
            raise CampaignNotFoundError

        await self.campaign_repository.delete_campaign(campaign_id, advertiser_id)

    async def get_advertiser_campaigns(
        self,
        advertiser_id: uuid.UUID,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[CampaignDTO]:
        campaigns = await self.campaign_repository.get_advertiser_campaigns(
            advertiser_id=advertiser_id,
            limit=limit,
            offset=offset,
        )

        return [
            CampaignDTO(
                id=campaign.id,
                impressions_limit=campaign.impressions_limit,
                clicks_limit=campaign.clicks_limit,
                cost_per_impression=campaign.cost_per_impression,
                cost_per_click=campaign.cost_per_click,
                ad_title=campaign.ad_title,
                ad_text=campaign.ad_text,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                advertiser_id=campaign.advertiser_id,
                targeting=TargetingDTO(
                    gender=campaign.targeting.gender,
                    age_from=campaign.targeting.age_from,
                    age_to=campaign.targeting.age_to,
                    location=campaign.targeting.location,
                )
                if campaign.targeting
                else None,
            )
            for campaign in campaigns
        ]

    async def moderate_campaign(self, campaign_id: uuid.UUID) -> None:
        campaign = await self.campaign_repository.get_campaign(campaign_id)

        if campaign is None:
            raise CampaignNotFoundError

        valid = await self.moderator.validate_text(campaign.ad_text)

        if not valid:
            campaign.ad_text = '[ MEGAZORDED ]'
            await self.campaign_repository.create_campaign(campaign, overwrite=True)

    async def pre_generate_campaign_description(
        self,
        advertiser_name: str,
        campaign_name: str,
    ) -> str:
        prompt = """
            Ты - генератор описаний для рекламных кампаний.
            На вход тебе подается имя рекламодателя и имя рекламной кампании.
            Генерируй подходящие описания рекламных кампаний.
            Возвращай JSON-ответ формата {"result": {str}"}
            """
        text = f'Имя рекламодателя: {advertiser_name}, имя кампании: {campaign_name}'

        return await self.text_generator.generate_text(prompt, text)


usecase_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
usecase_provider.provide(CampaignUsecase)
