import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.models.sqlalchemy import Base


class TelegramAdvertiser(Base):
    __tablename__ = 'telegram_advertisers'

    telegram_id: Mapped[uuid.UUID] = mapped_column(sa.String, primary_key=True)
    advertiser_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID,
        sa.ForeignKey('advertisers.id'),
        nullable=False,
        primary_key=True,
    )
    advertiser: Mapped['Advertiser'] = relationship(
        'Advertiser',
        back_populates='telegram_advertiser',
    )
