# Trace format

Truthy uses small append-only records so an investigation can be inspected with ordinary command-line tools.

## `trace.tsv`

Columns:

```text
utc\tkind\tkey\tvalue
```

`kind` examples: `new`, `search`, `fetch`, `links`, `model`, `claim`, `decision`, `issue`.

`key` is a stable local identifier when one exists: a URL, SHA-256 digest, model-run directory, claim id, or issue URL.

`value` is a single-line note.  Tabs and newlines are replaced with spaces before append.

The UTC timestamp describes when the step happened.  It is not part of a content identity.

## `edges.tsv`

```text
from_kind\tfrom_key\trelation\tto_kind\tto_key\tnote
```

This is the investigation graph.  It records branch points directly: search → URL, URL → frozen artifact, artifact → extracted URL, evidence → claim, prompt → model run, and any manual branch added with `truthy-edge`.  A linear trace is useful for chronology; `edges.tsv` preserves why one path teed off into another.

## `searches.tsv`

```text
utc\tprovider\tquery\tresult_url
```

Record searches even when the result is ultimately rejected.  Multiple result URLs may be appended for the same query.

## `claims.tsv`

Recommended columns:

```text
claim_id\tstatus\tclaim\tevidence\tnote
```

Suggested status vocabulary is descriptive rather than magical: `unreviewed`, `supported`, `contradicted`, `mixed`, `not-established`, `out-of-scope`.

`evidence` should point to a frozen artifact hash plus a location within it when practical.

## Artifact identity

Fetched bodies live at:

```text
artifacts/sha256/<sha256>/body
```

Fetch observations live below `fetches/` so a later request never overwrites the metadata from an earlier request that happened to return the same body hash.

The body hash is the identity.  URL is metadata because the same URL can change and the same body can be obtained from multiple URLs.

## Model run identity

Each run records:

```text
model-runs/<UTC>-<prompt-prefix>/
  model-id.txt
  model-revision.txt
  command.txt
  prompt.txt
  stdout.txt
  stderr.txt
  hashes.tsv
  exit-status.txt
```

A model revision label is required even if it is only a local commit/model-store identifier.  The runner does not claim bit-for-bit determinism; it preserves enough information to inspect and compare the run.
