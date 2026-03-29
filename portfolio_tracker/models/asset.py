from dataclasses import dataclass
from portfolio_tracker.utils.market_data import get_current_price


@dataclass
class Asset:
    ticker: str
    name: str
    sector: str
    asset_class: str
    quantity: float
    avg_purchase_price: float
    current_price: float = 0.0

    @classmethod
    def from_orders(cls, orders: list[dict]) -> "Asset":
        first = orders[0]
        total_qty = sum(o["quantity"] for o in orders)
        avg_price = sum(o["quantity"] * o["purchase_price"] for o in orders) / total_qty
        current_price = get_current_price(first["ticker"])

        return cls(
            ticker=first["ticker"],
            name=first["name"] or first["ticker"],
            sector=first["sector"],
            asset_class=first["asset_class"],
            quantity=total_qty,
            avg_purchase_price=avg_price,
            current_price=current_price,
        )

    @property
    def current_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def total_invested(self) -> float:
        return self.quantity * self.avg_purchase_price

    @property
    def gain_loss(self) -> float:
        return self.current_value - self.total_invested

    @property
    def gain_loss_pct(self) -> float:
        return (self.gain_loss / self.total_invested) * 100