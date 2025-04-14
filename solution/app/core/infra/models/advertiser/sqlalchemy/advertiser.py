import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.models.sqlalchemy import Base


class Advertiser(Base):
    __tablename__ = 'advertisers'

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        primary_key=True,
        unique=True,
    )
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.sql.func.now(),
    )

    scores: Mapped[list['Score']] = relationship(
        'Score',
        back_populates='advertiser',
        cascade='all, delete-orphan',
    )
    campaigns: Mapped[list['Campaign']] = relationship(
        'Campaign',
        back_populates='advertiser',
        cascade='all, delete-orphan',
    )
    telegram_advertiser: Mapped[list['TelegramAdvertiser']] = relationship(
        'TelegramAdvertiser',
        back_populates='advertiser',
        cascade='all, delete-orphan',
    )
