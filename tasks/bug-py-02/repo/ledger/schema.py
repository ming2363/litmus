"""门店与订单表。"""

import sqlite3


def connect() -> sqlite3.Connection:
    """打开一个内存库，供本进程内的报表使用。"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """创建报表需要的表。重复调用会先删掉旧表。"""
    conn.executescript(
        """
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS stores;
        CREATE TABLE stores (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            region TEXT NOT NULL
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            store_id INTEGER NOT NULL REFERENCES stores(id),
            status TEXT NOT NULL,
            amount_cents INTEGER,
            ordered_on TEXT NOT NULL
        );
        """
    )
    conn.commit()


def add_store(conn: sqlite3.Connection, store_id: int, name: str, region: str) -> None:
    conn.execute(
        "INSERT INTO stores (id, name, region) VALUES (?, ?, ?)",
        (store_id, name, region),
    )


def add_order(
    conn: sqlite3.Connection,
    order_id: int,
    store_id: int,
    status: str,
    amount_cents,
    ordered_on: str,
) -> None:
    conn.execute(
        """
        INSERT INTO orders (id, store_id, status, amount_cents, ordered_on)
        VALUES (?, ?, ?, ?, ?)
        """,
        (order_id, store_id, status, amount_cents, ordered_on),
    )
