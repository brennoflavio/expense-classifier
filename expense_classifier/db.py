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
        "create table if not exists credit_card (id bigserial primary key, purchase_date timestamp, description text, owner text, amount bigint, current_installment bigint, total_installments bigint, score bigint, category text, file_path text, headers text);",
        "create unique index if not exists idx_001 on credit_card (purchase_date, description, owner, amount);",
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


def upsert_data(data, file_path, headers):
    with db() as conn:
        insert_sql = "insert into credit_card (purchase_date, description, owner, amount, current_installment, total_installments, score, category, file_path, headers) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        check_sql = "select count(*) c from credit_card where purchase_date = %s and description = %s and owner = %s"

        cursor = conn.cursor()

        for row in data:
            cursor.execute(
                check_sql,
                (row.get("purchase_date"), row.get("description"), row.get("owner")),
            )
            c = cursor.fetchone()
            c = c[0]

            if int(c) > 0:
                logging.warn("attempt to insert a duplicate line")
                continue

            cursor.execute(
                insert_sql,
                (
                    row.get("purchase_date"),
                    row.get("description"),
                    row.get("owner"),
                    int(row.get("amount") * Decimal(100)),
                    row.get("current_installment"),
                    row.get("total_installments"),
                    row.get("score"),
                    row.get("category"),
                    file_path,
                    headers,
                ),
            )

        conn.commit()
