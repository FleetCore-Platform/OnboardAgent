import os
import urllib.request
from loguru import logger


def download_file(url: str, path: str) -> None:
    """
    Download file from url to path.
    Args:
        url (str): The url to download the file from.
        path (str): The path to save the file to.
    """
    if path.endswith("/"):
        path = path + "mission.bundle.zip"
    else:
        path = path + "/mission.bundle.zip"

    try:
        urllib.request.urlretrieve(url, path)
        logger.info(f"Downloading to path {path}")
    except Exception as e:
        logger.error(f"Couldn't download file: {e}")


def ensure_dir(path: str) -> None:
    """
    Ensure the directory exists.
    Args:
        path (str): The path of the directory to ensure exists.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        logger.warning(f"Creating directory {directory}, because it does not exist!")
        os.makedirs(directory)


def handle_download(url: str, path: str) -> tuple[int, str]:
    """
    Handle the file download process.
    Args:
        url (str): The url to download the file from.
        path (str): The path to save the file to.
    Returns:
        tuple: 0 if the process is successful, 1 otherwise, and the path to the saved file.
    """
    if path.startswith("/tmp"):
        ensure_dir(path)
    else:
        logger.error("Cannot download to a directory other than /tmp")
        return 1, ""

    try:
        download_file(url, path)

        if path.endswith("/"):
            path = path + "mission.bundle.zip"
        else:
            path = path + "/mission.bundle.zip"

        return 0, path
    except Exception as e:
        logger.error(f"Couldn't download file: {e}")
        return 1, ""
