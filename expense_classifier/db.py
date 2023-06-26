from env import POSTGRES_DATABASE, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_USERNAME
import psycopg
from contextlib import contextmanager
import logging
from decimal import Decimal


def reverse_migrate():
    logging.info("resetting database")
    migrations = ["drop table credit_card"]
    with db() as conn:
        cursor = conn.cursor()
        for migration in migrations:
            cursor.execute(migration)
        conn.commit()


def migrate():
    logging.info("running migrations")
    migrations = [
        "create table if not exists credit_card (id bigserial primary key, expected_payment_date timestamp, expected_payment_date_score bigint, purchase_date timestamp, description text, owner text, amount numeric, current_installment bigint, total_installments bigint, score bigint, category text, file_path text, headers text);",
    ]
    with db() as conn:
        cursor = conn.cursor()
        for migration in migrations:
            cursor.execute(migration)
        conn.commit()


def db():
    return psycopg.connect(
        f"dbname={POSTGRES_DATABASE} user={POSTGRES_USERNAME} password={POSTGRES_PASSWORD} host={POSTGRES_HOST}"
    )


def upsert_data(data, file_path, headers, expect_payment_date):
    with db() as conn:
        cursor = conn.cursor()

        delete_sql = "delete from credit_card where expected_payment_date = %s"
        cursor.execute(delete_sql, (expect_payment_date,))
        conn.commit()

        insert_sql = "insert into credit_card (purchase_date, description, owner, amount, current_installment, total_installments, score, category, file_path, headers, expected_payment_date, expected_payment_date_score) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        for row in data:
            cursor.execute(
                insert_sql,
                (
                    row.get("purchase_date"),
                    row.get("description"),
                    row.get("owner"),
                    row.get("amount"),
                    row.get("current_installment"),
                    row.get("total_installments"),
                    row.get("score"),
                    row.get("category"),
                    file_path,
                    headers,
                    row.get("expected_payment_date"),
                    row.get("expected_payment_date_score"),
                ),
            )

        conn.commit()
