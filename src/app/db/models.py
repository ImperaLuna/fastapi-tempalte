import uuid

from sqlalchemy import Enum, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin
from app.domain.order import OrderStatus


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    # uuid7 is time-ordered: new rows land at the end of the primary key
    # index instead of at random positions (uuid4's index-thrashing problem).
    # Generated client-side so entities have identity before persisting;
    # the server default covers writers that bypass the app (psql, backfills).
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid7, server_default=text("uuidv7()")
    )

    # Stored as VARCHAR + CHECK constraint, not a native Postgres ENUM:
    # native enums make adding/removing values a migration headache
    # (ALTER TYPE), while a CHECK constraint is just dropped and recreated.
    # create_constraint=True matters — without it (the default since
    # SQLAlchemy 1.4) the column is a bare VARCHAR and nothing is enforced.
    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            native_enum=False,
            create_constraint=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=OrderStatus.DRAFT,
    )
