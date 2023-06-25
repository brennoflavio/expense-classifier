from webdav3.client import Client
from env import (
    NEXTCLOUD_DAV_ENDPOINT,
    NEXTCLOUD_FOLDER,
    NEXTCLOUD_PASSWORD,
    NEXTCLOUD_USERNAME,
)
from tempfile import NamedTemporaryFile
import os
import csv


def build_dav_file_path(path):
    return os.path.join(NEXTCLOUD_FOLDER, path)


def get_dav_client():
    options = {
        "webdav_hostname": NEXTCLOUD_DAV_ENDPOINT,
        "webdav_login": NEXTCLOUD_USERNAME,
        "webdav_password": NEXTCLOUD_PASSWORD,
    }
    client = Client(options)
    client.verify = True
    return client


def get_one_file():
    client = get_dav_client()
    file_list = client.list(NEXTCLOUD_FOLDER)

    for f in file_list:
        if ".csv" in f:
            with NamedTemporaryFile("w") as temp_file:
                client.download_sync(
                    remote_path=build_dav_file_path(f),
                    local_path=temp_file.name,
                )

                with open(temp_file.name) as opened_temp_file:
                    reader = [x for x in csv.reader(opened_temp_file, delimiter=";")]
                    headers = reader[0]
                    data = reader[1:]
                    return build_dav_file_path(f), data, headers

    return None, None, None


def delete_file(f):
    client = get_dav_client()
    client.clean(f)


if __name__ == "__main__":
    print(get_one_file())
