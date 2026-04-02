import sys

import gql
from gql.transport.requests import RequestsHTTPTransport


def main() -> int:
    (owner, name) = ("microsoft", "TypeScript")
    query = gql.GraphQLRequest(
        """
        query PullRequests($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name, followRenames: true) {
            pullRequests(first: 100) {
              nodes {
                permalink
              }
            }
          }
        }
        """,
        variable_values={"owner": owner, "name": name},
    )

    transport = RequestsHTTPTransport(
        url="https://api.github.com/graphql",
        timeout=3,
    )
    client = gql.Client(transport=transport)

    result = client.execute(query)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
