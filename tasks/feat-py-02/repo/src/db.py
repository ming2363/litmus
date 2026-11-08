"""SQLite 数据库建表与示例数据辅助函数。"""

import sqlite3
from typing import Iterable, Tuple

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    monthly_cents INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    plan_id INTEGER NOT NULL,
    billed_at TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);

CREATE TABLE IF NOT EXISTS refunds (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL,
    refunded_at TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);
"""


def create_memory_db() -> sqlite3.Connection:
    """创建并初始化内存 SQLite 数据库。"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)
    return conn


def seed_customers(conn: sqlite3.Connection, rows: Iterable[Tuple[int, str, str]]) -> None:
    conn.executemany("INSERT INTO customers (id, name, region) VALUES (?, ?, ?)", list(rows))
    conn.commit()


def seed_plans(conn: sqlite3.Connection, rows: Iterable[Tuple[int, str, int]]) -> None:
    conn.executemany("INSERT INTO plans (id, code, monthly_cents) VALUES (?, ?, ?)", list(rows))
    conn.commit()


def seed_invoices(
    conn: sqlite3.Connection, rows: Iterable[Tuple[int, int, int, str, int, str]]
) -> None:
    conn.executemany(
        "INSERT INTO invoices (id, customer_id, plan_id, billed_at, amount_cents, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        list(rows),
    )
    conn.commit()


def seed_refunds(conn: sqlite3.Connection, rows: Iterable[Tuple[int, int, str, int]]) -> None:
    conn.executemany(
        "INSERT INTO refunds (id, invoice_id, refunded_at, amount_cents) VALUES (?, ?, ?, ?)",
        list(rows),
    )
    conn.commit()
