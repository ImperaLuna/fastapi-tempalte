from enum import StrEnum


class OrderStatus(StrEnum):
    """Lifecycle states of an order.

    The transition rules (which state may move to which) will live here in the
    domain layer as the state machine — the database only stores the value.
    """

    DRAFT = "draft"
    PLACED = "placed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
