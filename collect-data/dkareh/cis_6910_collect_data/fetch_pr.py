import contextlib
import json
import os
import sys
from pathlib import Path
from typing import NewType

import gql
from gql.transport.requests import RequestsHTTPTransport

_Cursor = NewType("_Cursor", str)
type _FullName = tuple[str, str]
type _Entry = tuple[_FullName, _Cursor | None]
type _State = list[_Entry]


def _load_entry(data) -> _Entry:
    # Convert lists to tuples.
    [full_name, cursor] = data
    return (tuple(full_name), cursor)


def _load_state(path: Path) -> _State:
    with path.open("rb") as file:
        return list(map(_load_entry, json.load(file)))


def _dump_state(path: Path, state: _State):
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(state, file, ensure_ascii=False, separators=(",", ":"))


_QUERY = """
  query PullRequests($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name, followRenames: true) {
      pullRequests(first: 100) {
        nodes {
          permalink
        }
      }
    }
  }
"""


def main() -> int:
    root_directory = Path(__file__).parent / "../.."
    state_directory = root_directory / "state"
    state_path = state_directory / "fetch_pr.json"
    state = _load_state(state_path)

    (owner, name) = ("microsoft", "TypeScript")
    query = gql.GraphQLRequest(
        _QUERY,
        variable_values={"owner": owner, "name": name},
    )

    token = os.environ["GITHUB_GRAPHQL_TOKEN"]
    transport = RequestsHTTPTransport(
        url="https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {token}"},
        timeout=3,
    )
    client = gql.Client(transport=transport)

    with contextlib.ExitStack() as stack:
        session = stack.enter_context(client)
        _ = stack.callback(_dump_state, state_path, state)
        result = session.execute(query)
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
