import pydantic
import pydantic_settings


class Config(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file='.env',
        env_ignore_empty=True,
        extra='ignore',
    )

    MODERATE_TEXTS: bool = pydantic.Field(default=False)

    TOKEN_TELEGRAM_API: str = pydantic.Field(default='')

    POSTGRES_USERNAME: str = pydantic.Field(default='postgres')
    POSTGRES_PASSWORD: str = pydantic.Field(default='postgres')
    POSTGRES_HOST: str = pydantic.Field(default='localhost')
    POSTGRES_PORT: int = pydantic.Field(default=5432)
    POSTGRES_DATABASE: str = pydantic.Field(default='postgres')

    YANDEX_GPT_CATALOG_IDENTIFIER: str = pydantic.Field(default='')
    YANDEX_GPT_API_KEY: str = pydantic.Field(default='')

    S3_KEY_IDENTIFIER: str = pydantic.Field(default='')
    S3_KEY: str = pydantic.Field(default='')
    S3_BUCKET: str = pydantic.Field(default='')

    DEBUG: bool = pydantic.Field(default=False)


config = Config()

psycopg_url = f'postgresql+psycopg://{config.POSTGRES_USERNAME}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DATABASE}'
