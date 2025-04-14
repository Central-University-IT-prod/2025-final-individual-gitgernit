import enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.infra.models.sqlalchemy import Base


class AvailableOptions(enum.StrEnum):
    DAY = 'DAY'


class Options(Base):
    __tablename__ = 'options'

    option: Mapped[AvailableOptions] = mapped_column(
        sa.Enum(AvailableOptions),
        nullable=False,
        primary_key=True,
    )
    value: Mapped[str] = mapped_column(sa.String, nullable=True)
