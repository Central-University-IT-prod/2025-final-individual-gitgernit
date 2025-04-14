import dishka.integrations.aiogram
import dishka.integrations.fastapi

import app.core.config
import app.core.domain.advertiser.service.usecases
import app.core.domain.campaign.service.usecases
import app.core.domain.client.service.usecases
import app.core.domain.feed.service.usecases
import app.core.domain.options.service.dto
import app.core.domain.options.service.usecases
import app.core.domain.score.service.usecases
import app.core.domain.stats.service.usecases
import app.core.domain.storage.service.usecases
import app.core.infra.models.advertiser.sqlalchemy.repository as advertiser_repository
import app.core.infra.models.campaign.sqlalchemy.repository as campaign_repository
import app.core.infra.models.click.sqlalchemy.repository as clicks_repository
import app.core.infra.models.client.sqlalchemy.repository as client_repository
import app.core.infra.models.impression.sqlalchemy.repository as impressions_repository
import app.core.infra.models.options.sqlalchemy.repository as options_repository
import app.core.infra.models.score.sqlalchemy.repository as score_repository
import app.core.infra.models.sqlalchemy.providers as sqlalchemy_providers
import app.core.infra.models.telegram_advertisers.sqlalchemy.repository as telegram_advertisers_repository  # noqa
import app.core.infra.storage.s3.repository as storage_providers
import app.core.infra.text_generators.yandexgpt as generator_providers
import app.core.infra.yandexgpt.interactors as yandexgpt_providers

if app.core.config.config.MODERATE_TEXTS:
    import app.core.infra.moderation.yandexgpt as moderator_providers

else:
    import app.core.infra.moderation.mock as moderator_providers

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
    app.core.domain.client.service.usecases.usecase_provider,
    app.core.domain.advertiser.service.usecases.usecase_provider,
    app.core.domain.score.service.usecases.usecase_provider,
    app.core.domain.campaign.service.usecases.usecase_provider,
    app.core.domain.options.service.usecases.usecase_provider,
    app.core.domain.feed.service.usecases.usecase_provider,
    app.core.domain.stats.service.usecases.usecase_provider,
    app.core.domain.storage.service.usecases.usecase_provider,
    sqlalchemy_providers.EngineProvider(app.core.config.psycopg_url),
    sqlalchemy_providers.SessionProvider(),
    yandexgpt_providers.InteractorProvider(
        catalog_identifier=app.core.config.config.YANDEX_GPT_CATALOG_IDENTIFIER,
        api_key=app.core.config.config.YANDEX_GPT_API_KEY,
    ),
    moderator_providers.moderator_provider,
    generator_providers.generator_provider,
    storage_providers.StorageProvider(
        app.core.config.config.S3_KEY_IDENTIFIER,
        app.core.config.config.S3_KEY,
        app.core.config.config.S3_BUCKET,
    ),
)
