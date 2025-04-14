__all__ = ['Base', 'load_models']

import sqlalchemy.ext.declarative

Base: sqlalchemy.ext.declarative.DeclarativeMeta = (
    sqlalchemy.ext.declarative.declarative_base()
)


def load_models() -> None:
    import app.core.infra.models.advertiser.sqlalchemy.advertiser
    import app.core.infra.models.campaign.sqlalchemy.campaign
    import app.core.infra.models.click.sqlalchemy.click
    import app.core.infra.models.client.sqlalchemy.client
    import app.core.infra.models.impression.sqlalchemy.impression
    import app.core.infra.models.options.sqlalchemy.options
    import app.core.infra.models.score.sqlalchemy.score
    import app.core.infra.models.telegram_advertisers.sqlalchemy.telegram_advertiser
