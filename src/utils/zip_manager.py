import os
from zipfile import ZipFile


def extract_mission(thing_name: str, path: str) -> str | None:
    out_path = os.path.join(path, thing_name)

    try:
        with ZipFile(path) as archive:
            archive.extract(member=thing_name, path=out_path)

        return out_path

    except Exception as e:
        print(e)
        return None
