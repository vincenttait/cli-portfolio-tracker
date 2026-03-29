import sqlite3
from pathlib import Path

DB_FILE = Path("portfolio_tracker/data/portfolio.db")
SCHEMA_FILE = Path("schema.sql")


def init_db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        conn.executescript(SCHEMA_FILE.read_text())


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def load_assets():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM assets").fetchall()
        return [dict(row) for row in rows]


def save_asset(asset: dict):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO assets (ticker, name, sector, asset_class, quantity, purchase_price, purchase_date)
            VALUES (:ticker, :name, :sector, :asset_class, :quantity, :purchase_price, :purchase_date)
        """, asset)


def delete_asset(asset_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))


def update_asset(asset_id: int, asset: dict):
    with get_connection() as conn:
        conn.execute("""
            UPDATE assets
            SET ticker         = :ticker,
                name           = :name,
                sector         = :sector,
                asset_class    = :asset_class,
                quantity       = :quantity,
                purchase_price = :purchase_price,
                purchase_date  = :purchase_date
            WHERE id = :id
        """, {**asset, "id": asset_id})