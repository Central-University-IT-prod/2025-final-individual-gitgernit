import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.models.sqlalchemy import Base


class Score(Base):
    __tablename__ = 'score'

    client_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey('clients.id'),
        primary_key=True,
        nullable=False,
    )
    advertiser_id: Mapped[uuid.UUID] = mapped_column(
        sa.ForeignKey('advertisers.id'),
        primary_key=True,
        nullable=False,
    )
    score: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.sql.func.now(),
    )

    client = relationship('Client', back_populates='scores')
    advertiser = relationship('Advertiser', back_populates='scores')
