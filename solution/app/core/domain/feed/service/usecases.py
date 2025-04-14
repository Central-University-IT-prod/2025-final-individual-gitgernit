import uuid
from typing import TYPE_CHECKING

import dishka

from app.core.domain.campaign.entities.repositories import CampaignRepository
from app.core.domain.campaign.service.dto import CampaignDTO, TargetingDTO
from app.core.domain.client.entities.repositories import ClientRepository
from app.core.domain.feed.entities.entities import CampaignClick, CampaignImpression
from app.core.domain.feed.entities.repositories import (
    ClicksRepository,
    ImpressionsRepository,
)
from app.core.domain.options.entities.entities import AvailableOptions
from app.core.domain.options.entities.repositories import OptionsRepository
from app.core.domain.score.entities.repositories import ScoreRepository

if TYPE_CHECKING:
    from app.core.domain.campaign.entities.entities import Campaign


class ClientNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__('No such client found.')


class CampaignNotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__('No campaign found.')


class CampaignInactiveError(Exception):
    def __init__(self) -> None:
        super().__init__('Given campaign is inactive (by any means).')


class NotAllowedError(Exception):
    def __init__(self) -> None:
        super().__init__('Client is not allowed to do this action.')


class FeedUsecase:
    def __init__(
        self,
        campaign_repository: CampaignRepository,
        client_repository: ClientRepository,
        score_repository: ScoreRepository,
        options_repository: OptionsRepository,
        impressions_repository: ImpressionsRepository,
        clicks_repository: ClicksRepository,
    ) -> None:
        self.client_repository = client_repository
        self.campaign_repository = campaign_repository
        self.score_repository = score_repository
        self.options_repository = options_repository
        self.impressions_repository = impressions_repository
        self.clicks_repository = clicks_repository

    async def get_best_campaign(
        self,
        client_id: uuid.UUID,
    ) -> CampaignDTO:
        current_day = int(
            (await self.options_repository.get_option(AvailableOptions.DAY)).value,
        )
        client = await self.client_repository.get_client(client_id)

        if client is None:
            raise ClientNotFoundError

        targeted_campaigns = await self.campaign_repository.get_targeted_campaigns(
            age=client.age,
            location=client.location,
            gender=client.gender,
        )
        active_campaigns: list[
            tuple[Campaign, bool]
        ] = []  # campaign & viewed by client

        for campaign in targeted_campaigns:
            if not await campaign.started(current_day) or await campaign.ended(
                current_day,
            ):
                continue

            impressions = await self.impressions_repository.get_campaign_impressions(
                campaign.id,
            )
            clicks = await self.clicks_repository.get_campaign_clicks(campaign.id)

            if len(impressions) >= campaign.impressions_limit:
                continue

            # if len(clicks) >= campaign.clicks_limit:
            #     continue

            viewed = False

            if any(impression.client_id == client_id for impression in impressions):
                viewed = True

            active_campaigns.append((campaign, viewed))

        if not active_campaigns:
            raise CampaignNotFoundError

        campaign_score_pairs: list[
            tuple[Campaign, bool, int]
        ] = []  # campaign, viewed, score

        for campaign_viewed_pair in active_campaigns:
            campaign, viewed = campaign_viewed_pair

            ml_score = await self.score_repository.get_score(
                client_id,
                campaign.advertiser_id,
            )

            score = ml_score.score if ml_score else 0

            campaign_score_pairs.append(
                (
                    campaign,
                    viewed,
                    score,
                ),
            )

        best_score = max(campaign_score_pairs, key=lambda pair: pair[2])[2]
        best_impression_price = max(
            campaign_score_pairs,
            key=lambda pair: pair[0].cost_per_impression,
        )[0].cost_per_impression
        best_click_price = max(
            campaign_score_pairs,
            key=lambda pair: pair[0].cost_per_click,
        )[0].cost_per_click

        best_pairs = sorted(
            campaign_score_pairs,
            key=lambda pair: (
                pair[1],
                -(
                    (
                        (
                            (pair[0].cost_per_impression / best_impression_price)
                            if best_impression_price
                            else 0
                        )
                        + (
                            (pair[0].cost_per_click / best_click_price)
                            if best_click_price
                            else 0
                        )
                    )
                    * 2
                    + ((pair[2] / best_score) if best_score else 0)
                ),
            ),
        )
        best_campaign, viewed, best_score = best_pairs[0]

        if viewed:
            best_pairs = sorted(best_pairs, key=lambda pair: -pair[2])
            best_campaign, viewed, best_score = best_pairs[0]

        if not viewed:
            new_impression = CampaignImpression(
                day=current_day,
                cost=best_campaign.cost_per_impression,
                client_id=client_id,
                campaign_id=best_campaign.id,
            )
            await self.impressions_repository.create_impression(new_impression)

        return CampaignDTO(
            id=best_campaign.id,
            impressions_limit=best_campaign.impressions_limit,
            clicks_limit=best_campaign.clicks_limit,
            cost_per_impression=best_campaign.cost_per_impression,
            cost_per_click=best_campaign.cost_per_click,
            ad_title=best_campaign.ad_title,
            ad_text=best_campaign.ad_text,
            start_date=best_campaign.start_date,
            end_date=best_campaign.end_date,
            advertiser_id=best_campaign.advertiser_id,
            targeting=TargetingDTO(
                gender=best_campaign.targeting.gender,
                age_from=best_campaign.targeting.age_from,
                age_to=best_campaign.targeting.age_to,
                location=best_campaign.targeting.location,
            )
            if best_campaign.targeting
            else None,
        )

    async def click_campaign(
        self,
        client_id: uuid.UUID,
        campaign_id: uuid.UUID,
    ) -> None:
        if await self.client_repository.get_client(client_id) is None:
            raise ClientNotFoundError

        campaign = await self.campaign_repository.get_campaign(campaign_id)

        if campaign is None:
            raise CampaignNotFoundError

        current_day = int(
            (await self.options_repository.get_option(AvailableOptions.DAY)).value,
        )

        if not await campaign.started(current_day) or await campaign.ended(current_day):
            raise CampaignInactiveError

        impressions = await self.impressions_repository.get_campaign_impressions(
            campaign_id,
            current_day,
        )

        if not any(impression.client_id == client_id for impression in impressions):
            raise NotAllowedError

        clicks = await self.clicks_repository.get_campaign_clicks(
            campaign_id,
            current_day,
        )
        #
        # if len(clicks) >= campaign.clicks_limit:
        #     raise NotAllowedError

        if not any(click.client_id == client_id for click in clicks):
            click = CampaignClick(
                day=current_day,
                cost=campaign.cost_per_click,
                client_id=client_id,
                campaign_id=campaign_id,
            )
            await self.clicks_repository.create_click(click)


usecase_provider = dishka.Provider(scope=dishka.Scope.REQUEST)
usecase_provider.provide(FeedUsecase)
