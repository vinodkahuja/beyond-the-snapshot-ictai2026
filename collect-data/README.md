# cis-6910-collect-data

## Installation

**Prerequisites:**
- An implementation of Python 3.14 or later
- A Python package manager (pip, PDM, Poetry, uv, etc.)

Then follow the standard process:
1. Download the project. If you need a `requirements.txt` file, download a
   tagged commit ([`ictai-2026`][1]) instead of the latest commit.

2. Install the dependencies.

3. Optionally install the project itself.

## Usage

**Note:** I generally recommend running Python scripts as submodules so that
relative imports work. That is, use `python -m`, `uv run --module`, etc.

1. Run `fetch_aidev_repository.py`:
   ```shell
   python -m dkareh.cis_6910_collect_data.fetch_aidev_repository
   ```
   This script will download the `all_repository.parquet` file from the [AIDev
   dataset](https://huggingface.co/datasets/hao-li/AIDev). If you prefer,
   you can manually download the file (revision `512e07014`) and move it to
   `input/all_repository.parquet`.

2. Next, run `fetch_pr_init.py` to initialize the collection state. The state
   file (`state/fetch_pr.json`) stores GraphQL pagination cursors.

3. Then, run `fetch_pr.py` to begin downloading data into `output/`. Pass a
   GitHub API token through the `GITHUB_GRAPHQL_TOKEN` environment variable.

If `fetch_pr.py` exits unexpectedly, you can resume data collection by
re-running the module (as long as the state file is intact).

Please note that the collection code does not perform any deduplication; the
output files may contain multiple, different entries for the same PR.

The `output/` directory will contain one or more files per repository in the
[JSON Lines](https://jsonlines.org/) format. Merge them using a tool of your
choice. For instance, to merge files for `microsoft/TypeScript` using `jq`:

```shell
jq --slurp --compact-output '{
  repository: {
    nameWithOwner: "microsoft/TypeScript",
    pullRequests: { nodes: add(.[].repository.pullRequests.nodes) }
  }
}' output/microsoft+TypeScript+*.jsonl > output/microsoft+TypeScript.json
```

---

I did not use any LLMs to create this project.

[1]: https://gitlab.com/dkareh/cis-6910-collect-data/-/tags/ictai-2026
