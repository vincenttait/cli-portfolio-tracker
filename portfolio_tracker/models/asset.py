from dataclasses import dataclass
from portfolio_tracker.utils.market_data import get_price_in_eur


@dataclass
class Asset:
    ticker: str
    name: str
    sector: str
    asset_class: str
    quantity: float
    avg_purchase_price: float
    currency: str
    current_price_local: float = 0.0
    current_price_eur: float   = 0.0

    @classmethod
    def from_orders(cls, orders: list[dict]) -> "Asset":
        """Aggregate multiple orders for the same ticker into a single position."""
        first = orders[0]
        total_qty = sum(o["quantity"] for o in orders)
        # Weighted average: accounts for orders at different prices and quantities
        avg_price = sum(o["quantity"] * o["purchase_price"] for o in orders) / total_qty
        local_price, currency, eur_price = get_price_in_eur(first["ticker"])

        return cls(
            ticker=first["ticker"],
            name=first["name"] or first["ticker"],
            sector=first["sector"],
            asset_class=first["asset_class"],
            quantity=total_qty,
            avg_purchase_price=avg_price,
            currency=currency,
            current_price_local=local_price,
            current_price_eur=eur_price,
        )

    @property
    def current_value_eur(self) -> float:
        return self.quantity * self.current_price_eur

    @property
    def total_invested_eur(self) -> float:
        """
        Note: avg_purchase_price is stored in local currency.
        We convert to EUR using the current FX rate as an approximation.
        """
        from portfolio_tracker.utils.market_data import get_fx_rate
        fx_rate = get_fx_rate(self.currency)
        return self.quantity * self.avg_purchase_price * fx_rate

    @property
    def gain_loss_eur(self) -> float:
        return self.current_value_eur - self.total_invested_eur

    @property
    def gain_loss_pct(self) -> float:
        return (self.gain_loss_eur / self.total_invested_eur) * 100