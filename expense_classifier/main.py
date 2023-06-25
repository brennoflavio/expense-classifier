from classifier import classify_file_data
from db import upsert_data, migrate, reverse_migrate
from webdav import get_one_file, delete_file
import logging


def run():
    # reverse_migrate()
    migrate()

    file_path, data, headers = get_one_file()
    if not data:
        logging.info("found no files, skipping")
        return

    logging.info(f"file_path = {file_path}, headers = {headers}")

    data = classify_file_data(data)
    upsert_data(data, file_path, headers)

    delete_file(file_path)


def main():
    logging.basicConfig(
        filename="expense_clssifier.log", encoding="utf-8", level=logging.INFO
    )
    run()


if __name__ == "__main__":
    main()
