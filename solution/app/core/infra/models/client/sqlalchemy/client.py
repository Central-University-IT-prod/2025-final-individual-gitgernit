import datetime
import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infra.models.sqlalchemy import Base


class ClientGender(enum.Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'


class Client(Base):
    __tablename__ = 'clients'

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        primary_key=True,
        unique=True,
    )
    login: Mapped[str] = mapped_column(sa.String, nullable=False)
    age: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    location: Mapped[str] = mapped_column(sa.String, nullable=False)
    gender: Mapped[ClientGender] = mapped_column(sa.Enum(ClientGender), nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.sql.func.now(),
    )

    scores: Mapped[list['Score']] = relationship(
        'Score',
        back_populates='client',
        cascade='all, delete-orphan',
    )
    impressions: Mapped[list['Impression']] = relationship(
        'Impression',
        back_populates='client',
    )
    clicks: Mapped[list['Click']] = relationship(
        'Click',
        back_populates='client',
    )
