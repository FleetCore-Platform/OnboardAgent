import os
import urllib.request


def download_file(url: str, path: str) -> None:
    if path.endswith("/"):
        path = path + "mission.bundle.zip"
    else:
        path = path + "/mission.bundle.zip"

    try:
        urllib.request.urlretrieve(url, path)
    except Exception as e:
        print("Couldn't download file: ", e)


def ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def handle_download(url: str, path: str) -> int:
    if path.startswith("/tmp"):
        ensure_dir(path)
    else:
        print("Cannot download to a directory other than /tmp")
        return 1

    try:
        download_file(url, path)
        return 0
    except Exception as e:
        print("Couldn't download file: ", e)
        return 1
