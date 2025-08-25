import urllib.request
import sys

args: list[str] = sys.argv
args.pop(0)

def download_file(url: str, path: str) -> None:
    if path.endswith("/"):
        path = path + "mission.bundle.zip"
    else:
        path = path + "/mission.bundle.zip"

    try:
        urllib.request.urlretrieve(url, path)
    except Exception as e:
        print("Couldn't download file: ", e)

def main() -> int:
    if len(args) > 1:
        download_file(args[0], args[1])
        return 0
    else:
        print("Usage: download-handler.py <url> <output>")
        return 1

if __name__ == "__main__":
    sys.exit(main())