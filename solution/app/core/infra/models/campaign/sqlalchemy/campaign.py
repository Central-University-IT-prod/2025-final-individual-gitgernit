import datetime
import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.models.sqlalchemy import Base


class CampaignGender(enum.StrEnum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    ALL = 'ALL'


class Campaign(Base):
    __tablename__ = 'campaigns'

    id: Mapped[uuid.UUID] = mapped_column(sa.UUID, primary_key=True, default=uuid.uuid4)

    impressions_limit: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    clicks_limit: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    cost_per_impression: Mapped[float] = mapped_column(sa.Float, nullable=False)
    cost_per_click: Mapped[float] = mapped_column(sa.Float, nullable=False)

    ad_title: Mapped[str] = mapped_column(sa.String, nullable=False)
    ad_text: Mapped[str] = mapped_column(sa.Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(
        sa.String,
        default=None,
        nullable=True,
    )

    start_date: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    end_date: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.sql.func.now(),
    )

    advertiser_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID,
        sa.ForeignKey('advertisers.id'),
        nullable=False,
    )
    advertiser: Mapped['Advertiser'] = relationship(
        'Advertiser',
        back_populates='campaigns',
    )

    gender: Mapped[CampaignGender | None] = mapped_column(
        sa.Enum(CampaignGender),
        default=None,
        nullable=True,
    )
    age_from: Mapped[int | None] = mapped_column(
        sa.Integer,
        default=None,
        nullable=True,
    )
    age_to: Mapped[int | None] = mapped_column(sa.Integer, default=None, nullable=True)
    location: Mapped[str | None] = mapped_column(sa.String, default=None, nullable=True)

    impressions: Mapped[list['Impression']] = relationship(
        'Impression',
        back_populates='campaign',
        cascade='all, delete-orphan',
    )
    clicks: Mapped[list['Click']] = relationship(
        'Click',
        back_populates='campaign',
        cascade='all, delete-orphan',
    )
