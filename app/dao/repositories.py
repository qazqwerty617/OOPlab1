from __future__ import annotations

from decimal import Decimal

from app.dao.base import BaseDAO
from app.models.entities import Invoice, Service, Subscriber


class UserDAO(BaseDAO):
    """DAO for application users. Uses explicit SQL and psycopg only."""

    def authenticate(self, username: str, password: str) -> bool:
        with self._connection_factory() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE username = %s AND password = %s",
                (username, password),
            ).fetchone()
            return row is not None


class SubscriberDAO(BaseDAO):
    """DAO for telephone station subscribers."""

    def all(self) -> list[Subscriber]:
        with self._connection_factory() as conn:
            rows = conn.execute(
                "SELECT id, full_name, phone_number, address, is_blocked "
                "FROM subscribers ORDER BY id DESC"
            ).fetchall()
            return [
                Subscriber(
                    id=row["id"],
                    full_name=row["full_name"],
                    phone_number=row["phone_number"],
                    address=row["address"],
                    is_blocked=bool(row["is_blocked"]),
                )
                for row in rows
            ]

    def get(self, subscriber_id: int) -> Subscriber | None:
        with self._connection_factory() as conn:
            row = conn.execute(
                "SELECT id, full_name, phone_number, address, is_blocked "
                "FROM subscribers WHERE id = %s",
                (subscriber_id,),
            ).fetchone()
            if row is None:
                return None
            return Subscriber(
                id=row["id"],
                full_name=row["full_name"],
                phone_number=row["phone_number"],
                address=row["address"],
                is_blocked=bool(row["is_blocked"]),
            )

    def create(self, item: Subscriber) -> Subscriber:
        with self._connection_factory() as conn:
            row = conn.execute(
                """
                INSERT INTO subscribers(full_name, phone_number, address, is_blocked)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (item.full_name, item.phone_number, item.address, item.is_blocked),
            ).fetchone()
            item.id = row["id"]
            return item

    def update(self, item: Subscriber) -> Subscriber:
        if item.id is None:
            raise ValueError("Subscriber id is required for update")
        with self._connection_factory() as conn:
            conn.execute(
                """
                UPDATE subscribers
                SET full_name = %s, phone_number = %s, address = %s, is_blocked = %s
                WHERE id = %s
                """,
                (item.full_name, item.phone_number, item.address, item.is_blocked, item.id),
            )
            return item

    def block(self, subscriber_id: int) -> None:
        with self._connection_factory() as conn:
            conn.execute(
                "UPDATE subscribers SET is_blocked = TRUE WHERE id = %s",
                (subscriber_id,),
            )

    def delete(self, subscriber_id: int) -> None:
        with self._connection_factory() as conn:
            conn.execute("DELETE FROM subscribers WHERE id = %s", (subscriber_id,))


class ServiceDAO(BaseDAO):
    """DAO for telephone services."""

    def all(self) -> list[Service]:
        with self._connection_factory() as conn:
            rows = conn.execute(
                "SELECT id, name, monthly_price FROM services ORDER BY name"
            ).fetchall()
            return [
                Service(row["id"], row["name"], Decimal(str(row["monthly_price"])))
                for row in rows
            ]

    def subscribe(self, subscriber_id: int, service_id: int) -> None:
        with self._connection_factory() as conn:
            conn.execute(
                """
                INSERT INTO subscriber_services(subscriber_id, service_id)
                VALUES (%s, %s)
                ON CONFLICT (subscriber_id, service_id) DO NOTHING
                """,
                (subscriber_id, service_id),
            )


class InvoiceDAO(BaseDAO):
    """DAO for invoices for calls and services."""

    def all_unpaid(self) -> list[dict]:
        with self._connection_factory() as conn:
            return conn.execute(
                """
                SELECT invoices.id, invoices.subscriber_id, invoices.amount,
                       invoices.description, invoices.is_paid, subscribers.full_name
                FROM invoices
                JOIN subscribers ON subscribers.id = invoices.subscriber_id
                WHERE invoices.is_paid = FALSE
                ORDER BY invoices.id DESC
                """
            ).fetchall()

    def create(self, invoice: Invoice) -> Invoice:
        with self._connection_factory() as conn:
            row = conn.execute(
                """
                INSERT INTO invoices(subscriber_id, amount, description, is_paid)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    invoice.subscriber_id,
                    invoice.amount,
                    invoice.description,
                    invoice.is_paid,
                ),
            ).fetchone()
            invoice.id = row["id"]
            return invoice

    def pay(self, invoice_id: int) -> None:
        with self._connection_factory() as conn:
            conn.execute(
                "UPDATE invoices SET is_paid = TRUE WHERE id = %s",
                (invoice_id,),
            )
