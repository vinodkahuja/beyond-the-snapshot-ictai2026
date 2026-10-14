# Beyond the Snapshot

*A Longitudinal Study of AI Agent Integration in Open-Source Software Development*

## Repository Structure

Updated files:
- `collect-data/`: Data collection code
- `data/`: Raw pull request data
- `dkareh/Analysis.ipynb`: Daniel's notebook, including the code to generate the
  `verification_sample_strict.csv` file
- `Analysis.ipynb`: Main analysis notebook
- `Agent Heuristic Verification (Strict).xlsx`: Updated verification results
- `verification_sample_strict.csv`: Updated sample of 200 PRs

Original files:
- `Agent Heuristic Verification.xlsx`: Old verification results
- `verification_sample.csv`: Old sample

## Data Collection Code

The `collect-data/` subdirectory was copied from [a personal repository on
GitLab][1]. This copy will remain mostly frozen even as the original source
receives updates. See [`collect-data/README.md`](collect-data/README.md) for
installation and usage directions.

## Data Format

Each repository gets a separate file under `data/`. The data is formatted
exactly like GitHub GraphQL API responses:
- `repository.nameWithOwner`: The repository's full name (e.g., "microsoft/TypeScript")
- `repository.pullRequests.nodes`: An array of PRs

The `nameWithOwner` field is redundant, but including it doesn't hurt. The
per-PR data includes only the fields listed in our paper.

[1]: https://gitlab.com/dkareh/cis-6910-collect-data
