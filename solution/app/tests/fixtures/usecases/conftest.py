import pytest

from app.core.domain.advertiser.service.usecases import AdvertiserUsecase
from app.core.domain.campaign.service.usecases import CampaignUsecase
from app.core.domain.client.service.usecases import ClientUsecase
from app.core.domain.feed.service.usecases import FeedUsecase
from app.core.domain.options.service.usecases import OptionsUsecase
from app.core.domain.score.service.usecases import ScoreUsecase
from app.core.domain.stats.service.usecases import StatsUsecase
from app.core.domain.storage.service.repositories import StorageRepository
from app.core.domain.storage.service.usecases import StorageUsecase
from app.core.infra.models.advertiser.memory.repository import AdvertiserRepository
from app.core.infra.models.campaign.memory.repository import CampaignRepository
from app.core.infra.models.click.memory.repository import ClicksRepository
from app.core.infra.models.client.memory.repository import ClientRepository
from app.core.infra.models.impression.memory.repository import ImpressionsRepository
from app.core.infra.models.options.memory.repository import OptionsRepository
from app.core.infra.models.score.memory.repository import ScoreRepository
from app.core.infra.moderation.mock import MockModerator
from app.core.infra.text_generators.mock import MockTextGenerator

# Initialize fixtures
from app.tests.fixtures.repositories.conftest import *  # noqa
from app.tests.fixtures.storages import *  # noqa
from app.tests.fixtures.yandexgpt.conftest import *  # noqa


@pytest.fixture
def advertiser_usecase(
    advertiser_repository: AdvertiserRepository,
) -> AdvertiserUsecase:
    return AdvertiserUsecase(advertiser_repository=advertiser_repository)


@pytest.fixture
def campaign_usecase(
    campaign_repository: CampaignRepository,
    advertiser_repository: AdvertiserRepository,
    options_repository: OptionsRepository,
    moderator: MockModerator,
    text_generator: MockTextGenerator,
) -> CampaignUsecase:
    return CampaignUsecase(
        campaign_repository=campaign_repository,
        advertiser_repository=advertiser_repository,
        options_repository=options_repository,
        moderator=moderator,
        text_generator=text_generator,
    )


@pytest.fixture
def client_usecase(client_repository: ClientRepository) -> ClientUsecase:
    return ClientUsecase(client_repository=client_repository)


@pytest.fixture
def feed_usecase(
    campaign_repository: CampaignRepository,
    client_repository: ClientRepository,
    score_repository: ScoreRepository,
    options_repository: OptionsRepository,
    impressions_repository: ImpressionsRepository,
    clicks_repository: ClicksRepository,
) -> FeedUsecase:
    return FeedUsecase(
        campaign_repository=campaign_repository,
        client_repository=client_repository,
        score_repository=score_repository,
        options_repository=options_repository,
        impressions_repository=impressions_repository,
        clicks_repository=clicks_repository,
    )


@pytest.fixture
def options_usecase(options_repository: OptionsRepository) -> OptionsUsecase:
    return OptionsUsecase(options_repository=options_repository)


@pytest.fixture
def score_usecase(
    score_repository: ScoreRepository,
    client_repository: ClientRepository,
    advertiser_repository: AdvertiserRepository,
) -> ScoreUsecase:
    return ScoreUsecase(
        score_repository=score_repository,
        client_repository=client_repository,
        advertiser_repository=advertiser_repository,
    )


@pytest.fixture
def stats_usecase(
    campaign_repository: CampaignRepository,
    options_repository: OptionsRepository,
    impressions_repository: ImpressionsRepository,
    clicks_repository: ClicksRepository,
) -> StatsUsecase:
    return StatsUsecase(
        campaign_repository=campaign_repository,
        options_repository=options_repository,
        impressions_repository=impressions_repository,
        clicks_repository=clicks_repository,
    )


@pytest.fixture
def storage_usecase(storage_repository: StorageRepository) -> StorageUsecase:
    return StorageUsecase(storage_repository=storage_repository)
