import contextlib
import json
import os
import sys
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import NewType, TextIO

import gql
from gql.transport.requests import RequestsHTTPTransport

_Cursor = NewType("_Cursor", str)
type _FullName = tuple[str, str]
type _Entry = tuple[_FullName, _Cursor | None]
type _State = deque[_Entry]


def _load_entry(data) -> _Entry:
    # Convert lists to tuples.
    [full_name, cursor] = data
    return (tuple(full_name), cursor)


def _load_state(path: Path) -> _State:
    with path.open("rb") as file:
        return deque(map(_load_entry, json.load(file)))


def _dump_state(path: Path, state: _State):
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(list(state), file, ensure_ascii=False, separators=(",", ":"))


def _create_file_map(directory: Path, state: _State):
    with contextlib.ExitStack() as stack:
        current_time = f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}"
        file_map: dict[_FullName, TextIO] = {}
        for full_name, _ in state:
            path = directory / f"{'+'.join(full_name)}+{current_time}.jsonl"
            file = path.open("x", encoding="utf-8", newline="\n")
            file = stack.enter_context(file)
            file_map[full_name] = file
        return (file_map, stack.pop_all().close)


_QUERY = """
  query PullRequests($owner: String!, $name: String!, $after: String) {
    repository(owner: $owner, name: $name, followRenames: true) {
      pullRequests(first: 100, after: $after) {
        nodes {
          additions
          deletions
          changedFiles
          closedAt
          createdAt
          headRefName
          id
          mergedAt
          permalink
          state
          totalCommentsCount
          timelineItems(first: 100, after: null, itemTypes: [
            CLOSED_EVENT,
            HEAD_REF_FORCE_PUSHED_EVENT,
            ISSUE_COMMENT,
            MERGED_EVENT,
            PULL_REQUEST_COMMIT,
            PULL_REQUEST_REVIEW,
            REOPENED_EVENT,
          ]) {
            nodes {
              __typename
              ... on ClosedEvent {
                createdAt
                stateReason
              }
              ... on HeadRefForcePushedEvent {
                createdAt
              }
              ... on IssueComment {
                createdAt
              }
              ... on MergedEvent {
                createdAt
              }
              ... on PullRequestCommit {
                commit {
                  authoredDate
                  committedDate
                  # I don't expect any commits to have >10 (co-)authors.
                  authors(first: 10, after: null) {
                    nodes {
                      email
                      name
                    }
                  }
                }
              }
              ... on PullRequestReview {
                submittedAt
              }
              ... on ReopenedEvent {
                createdAt
              }
            }
            pageInfo {
              hasNextPage
            }
          }
        }
        pageInfo {
          endCursor
          hasNextPage
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

    token = os.environ["GITHUB_GRAPHQL_TOKEN"]
    transport = RequestsHTTPTransport(
        url="https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    client = gql.Client(transport=transport)

    with contextlib.ExitStack() as stack:
        output_directory = root_directory / "output"
        (file_map, file_map_close) = _create_file_map(output_directory, state)
        _ = stack.callback(file_map_close)

        session = stack.enter_context(client)
        _ = stack.callback(_dump_state, state_path, state)

        while state:
            (full_name, cursor) = state[0]
            (owner, name) = full_name
            query = gql.GraphQLRequest(
                _QUERY, variable_values={"owner": owner, "name": name, "after": cursor}
            )
            result = session.execute(query)
            page_info = result["repository"]["pullRequests"].pop("pageInfo")

            file = file_map[full_name]
            json.dump(result, file, ensure_ascii=False, separators=(",", ":"))
            assert file.write("\n") == len("\n")
            file.flush()

            if page_info["hasNextPage"]:
                state[0] = (full_name, page_info["endCursor"])
                state.rotate(-1)
            else:
                _ = state.popleft()
    return 0


if __name__ == "__main__":
    sys.exit(main())
