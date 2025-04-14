import pytest

from app.core.infra.models.advertiser.memory.repository import (
    MemoryAdvertiserRepository,
)
from app.core.infra.models.campaign.memory.repository import MemoryCampaignRepository
from app.core.infra.models.click.memory.repository import MemoryClicksRepository
from app.core.infra.models.client.memory.repository import MemoryClientRepository
from app.core.infra.models.impression.memory.repository import (
    MemoryImpressionsRepository,
)
from app.core.infra.models.memory import MemoryStorage
from app.core.infra.models.options.memory.repository import MemoryOptionsRepository
from app.core.infra.models.score.memory.repository import MemoryScoreRepository


@pytest.fixture
def memory_storage() -> MemoryStorage:
    return MemoryStorage()


@pytest.fixture
def advertiser_repository(memory_storage: MemoryStorage) -> MemoryAdvertiserRepository:
    return MemoryAdvertiserRepository(memory_storage)


@pytest.fixture
def campaign_repository(memory_storage: MemoryStorage) -> MemoryCampaignRepository:
    return MemoryCampaignRepository(memory_storage)


@pytest.fixture
def client_repository(memory_storage: MemoryStorage) -> MemoryClientRepository:
    return MemoryClientRepository(memory_storage)


@pytest.fixture
def score_repository(memory_storage: MemoryStorage) -> MemoryScoreRepository:
    return MemoryScoreRepository(memory_storage)


@pytest.fixture
def clicks_repository(memory_storage: MemoryStorage) -> MemoryClicksRepository:
    return MemoryClicksRepository(memory_storage)


@pytest.fixture
def impressions_repository(
    memory_storage: MemoryStorage,
) -> MemoryImpressionsRepository:
    return MemoryImpressionsRepository(memory_storage)


@pytest.fixture
def options_repository(memory_storage: MemoryStorage) -> MemoryOptionsRepository:
    return MemoryOptionsRepository(memory_storage)
