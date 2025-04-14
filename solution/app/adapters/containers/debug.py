import pathlib

import dishka.integrations.aiogram
import dishka.integrations.fastapi

import app.core.domain.advertiser.service.usecases
import app.core.domain.campaign.service.usecases
import app.core.domain.client.service.usecases
import app.core.domain.feed.service.usecases
import app.core.domain.options.service.dto
import app.core.domain.options.service.usecases
import app.core.domain.score.service.usecases
import app.core.domain.stats.service.usecases
import app.core.domain.storage.service.usecases
import app.core.infra.models.advertiser.memory.repository as advertiser_repository
import app.core.infra.models.campaign.memory.repository as campaign_repository
import app.core.infra.models.click.memory.repository as clicks_repository
import app.core.infra.models.client.memory.repository as client_repository
import app.core.infra.models.impression.memory.repository as impressions_repository
import app.core.infra.models.memory as memory_providers
import app.core.infra.models.options.memory.repository as options_repository
import app.core.infra.models.score.memory.repository as score_repository
import app.core.infra.models.telegram_advertisers.memory.repository as telegram_advertisers_repository  # noqa
import app.core.infra.moderation.mock as moderator_providers
import app.core.infra.storage.filesystem.repository as storage_providers
import app.core.infra.text_generators.mock as generator_providers

container = dishka.make_async_container(
    dishka.integrations.fastapi.FastapiProvider(),
    dishka.integrations.aiogram.AiogramProvider(),
    client_repository.repository_provider,
    advertiser_repository.repository_provider,
    score_repository.repository_provider,
    campaign_repository.repository_provider,
    options_repository.repository_provider,
    impressions_repository.repository_provider,
    clicks_repository.repository_provider,
    telegram_advertisers_repository.repository_provider,
    memory_providers.StorageProvider(),
    app.core.domain.client.service.usecases.usecase_provider,
    app.core.domain.advertiser.service.usecases.usecase_provider,
    app.core.domain.score.service.usecases.usecase_provider,
    app.core.domain.campaign.service.usecases.usecase_provider,
    app.core.domain.options.service.usecases.usecase_provider,
    app.core.domain.feed.service.usecases.usecase_provider,
    app.core.domain.stats.service.usecases.usecase_provider,
    app.core.domain.storage.service.usecases.usecase_provider,
    moderator_providers.moderator_provider,
    generator_providers.generator_provider,
    storage_providers.StorageProvider(str(pathlib.Path(__file__).parent.parent.parent)),
)
