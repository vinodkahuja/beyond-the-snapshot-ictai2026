import json
import sys
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq

_TOP_N = 10


def main() -> int:
    # Read `all_repository.parquet`.
    root_directory = Path(__file__).parent / "../.."
    input_directory = root_directory / "input"
    with (input_directory / "all_repository.parquet").open("rb") as file:
        all_repo = pq.read_table(file, columns=["full_name", "stars"])

    # Get the top repositories by star count.
    all_repo_top_n = all_repo.sort_by([("stars", "descending")]).slice(length=_TOP_N)
    assert len(all_repo_top_n) == _TOP_N

    # Split each full name (`nameWithOwner` in GitHub's GraphQL API).
    full_name = pc.split_pattern(all_repo_top_n["full_name"], "/")
    full_name_length = pc.list_value_length(full_name)
    assert pc.all(pc.equal(full_name_length, 2))

    cursor = [None] * _TOP_N
    state = list(zip(full_name.to_pylist(), cursor, strict=True))

    state_directory = root_directory / "state"
    state_path = state_directory / "fetch_pr.json"
    with state_path.open("x", encoding="utf-8", newline="\n") as file:
        json.dump(state, file, ensure_ascii=False, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
