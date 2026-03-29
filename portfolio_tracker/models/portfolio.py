from collections import defaultdict
from portfolio_tracker.models.asset import Asset
from portfolio_tracker.utils.storage import load_assets


class Portfolio:
    def __init__(self):
        self.assets: list[Asset] = self._load()

    def _load(self) -> list[Asset]:
        rows = load_assets()
        grouped = defaultdict(list)
        for row in rows:
            grouped[row["ticker"]].append(row)
        return [Asset.from_orders(orders) for orders in grouped.values()]

    @property
    def total_value(self) -> float:
        return sum(a.current_value for a in self.assets)

    @property
    def total_invested(self) -> float:
        return sum(a.total_invested for a in self.assets)

    @property
    def total_gain_loss(self) -> float:
        return self.total_value - self.total_invested

    @property
    def total_gain_loss_pct(self) -> float:
        return (self.total_gain_loss / self.total_invested) * 100

    def get_weights(self) -> list[dict]:
        return [
            {
                "ticker": a.ticker,
                "weight": (a.current_value / self.total_value) * 100
            }
            for a in self.assets
        ]

    def get_sector_breakdown(self) -> dict[str, float]:
        breakdown = defaultdict(float)
        for a in self.assets:
            breakdown[a.sector] += (a.current_value / self.total_value) * 100
        return dict(breakdown)

    def get_asset_class_breakdown(self) -> dict[str, float]:
        breakdown = defaultdict(float)
        for a in self.assets:
            breakdown[a.asset_class] += (a.current_value / self.total_value) * 100
        return dict(breakdown)

    def get_summary(self) -> list[dict]:
        return [
            {
                "ticker":             a.ticker,
                "name":               a.name,
                "sector":             a.sector,
                "asset_class":        a.asset_class,
                "quantity":           a.quantity,
                "avg_purchase_price": a.avg_purchase_price,
                "current_price":      a.current_price,
                "current_value":      a.current_value,
                "total_invested":     a.total_invested,
                "gain_loss":          a.gain_loss,
                "gain_loss_pct":      a.gain_loss_pct,
                "weight":             (a.current_value / self.total_value) * 100,
            }
            for a in self.assets
        ]