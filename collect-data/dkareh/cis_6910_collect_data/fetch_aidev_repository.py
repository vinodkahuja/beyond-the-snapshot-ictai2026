import shutil
import sys
from http import HTTPStatus
from pathlib import Path

import urllib3

_ROOT_URL = "https://huggingface.co/datasets/hao-li/AIDev"
_REVISION = "512e07014b7b6e34cc1080372caa1c2bc054369d"
_NAME = "all_repository.parquet"


def main() -> int:
    response = urllib3.request(
        "GET",
        f"{_ROOT_URL}/resolve/{_REVISION}/{_NAME}",
        headers={"Accept": "application/octet-stream"},
        preload_content=False,
    )

    try:
        status = HTTPStatus(response.status)
    except ValueError:
        message = f"Hugging Face returned an unknown code: {response.status}"
        print(message, file=sys.stderr)
        return 1
    if status != HTTPStatus.OK:
        message = f"Hugging Face returned {status} ({status.phrase}), not 200 (OK)"
        print(message, file=sys.stderr)
        return 1

    root_directory = Path(__file__).parent / "../.."
    input_directory = root_directory / "input"
    with (input_directory / _NAME).open("xb") as file:
        shutil.copyfileobj(response, file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
