CREATE TABLE IF NOT EXISTS assets (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker         TEXT    NOT NULL,
    name           TEXT,
    sector         TEXT    NOT NULL,
    asset_class    TEXT    NOT NULL,
    quantity       REAL    NOT NULL,
    purchase_price REAL    NOT NULL,
    purchase_date  TEXT    NOT NULL DEFAULT (date('now'))
);