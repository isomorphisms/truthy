# Truthy

Truthy is a reproducible fact-investigation system.

It is not a service that returns a magic `true` or `false`. It leaves an inspectable trail from a question to the material used to answer it:

**question → searches → candidate URLs → frozen artifacts → extracted links → model runs → claims → disagreements → conclusion**

The important object is the trail. A conclusion may be wrong; the trail should still make it possible to see how it was reached, rerun the mechanical parts, inspect the exact inputs, and replace a bad step.

Truthy can feed evidence into Blackball or any other project, but Truthy owns the investigation machinery itself.

## Rules

1. **Wikipedia is an index, not the stopping point.** When a Wikipedia statement matters, follow the citations and inspect the cited source when possible.
2. **Freeze what was actually inspected.** Every fetched body is stored under its SHA-256 digest. Record the URL and response headers beside it.
3. **Record discovery, not just evidence.** Search queries, providers, candidate URLs, dead ends, rejected sources, and branch points belong in the trace.
4. **Separate observation from inference.** A fetched document, an extracted quotation, a model summary, and a conclusion are different records.
5. **Do not overstate reproducibility.** Live search results and websites change. LLM execution may also be nondeterministic. Truthy supports deterministic replay over frozen inputs and preserves raw model prompts/outputs and model revision labels.
6. **Use models as workers, not authorities.** A model may propose search terms, detect contradictions, classify claims, or summarize a source. Its output is evidence about what the model said, not evidence that the underlying claim is true.
7. **No automated Wikipedia editing or talk-page posting.** If an investigation finds a plausible Wikipedia error, create a Truthy issue with the trace and evidence. Human review can decide what, if anything, should be posted upstream.
8. **Keep the investigation graph visible.** Controlled spidering should expose every tee-off instead of recursively disappearing into the web and later emitting an answer.

## Investigation layout

`truthy-new NAME QUESTION...` creates:

```text
runs/NAME/
  question.txt
  trace.tsv
  searches.tsv
  claims.tsv
  edges.tsv
  conclusion.md
  artifacts/sha256/
  model-runs/
  queue/model/
  queue/done/
  issues/
```

The files are intentionally ordinary files. Append-only TSV records, an explicit investigation-edge graph, content-addressed blobs, atomic rename, and small process interfaces are preferred over a database.

## Basic use

```sh
sh bin/truthy-new runs/example \
  'Did source X actually support the sentence attributed to it?'

sh bin/truthy-search-log runs/example \
  wikipedia 'exact phrase from article' \
  'https://en.wikipedia.org/wiki/...'

sh bin/truthy-fetch runs/example \
  'https://example.org/source.html'

python3 bin/truthy-links.py \
  runs/example/artifacts/sha256/HASH/body \
  'https://example.org/source.html' \
  --run runs/example --artifact-hash HASH

sh bin/truthy-model runs/example \
  qwen CANDIDATE-REVISION -- /path/to/qwen-worker \
  < prompt.txt
```

`truthy-model` uses a small process contract: prompt on stdin, answer on stdout, diagnostics on stderr, nonzero exit on failure. This lets Qwen, GPT-OSS, Pythia, or any later model be compared without teaching Truthy a model-specific API.

## Replay model

Truthy has two kinds of replay:

- **frozen replay:** operate only on stored artifacts and stored model outputs; this should be deterministic modulo tool-version changes;
- **live replay:** repeat network fetches/searches/model runs and compare new hashes to the old ones; differences are findings, not silent replacements.

A live rerun never overwrites an old artifact just because the URL is the same.

## Controlled spidering

Truthy does not recursively crawl everything it can reach. Link extraction emits a sorted, deduplicated candidate list. A caller or model can rank candidates, but only explicitly selected URLs are fetched. Depth, host boundaries, and fetch budgets can therefore be enforced by the process that drains the queue.

This is deliberate: an investigation should have a visible branching structure, not a crawler that disappears into the web and later emits an answer.

## Wikipedia discrepancy path

When Wikipedia appears wrong:

1. freeze the relevant Wikipedia revision or page response;
2. identify the exact sentence/claim;
3. follow and freeze the cited source(s);
4. record whether the source supports, contradicts, or fails to establish the claim;
5. look for upstream/primary evidence and credible disagreement;
6. write the conclusion with uncertainty and scope;
7. create a Truthy issue using `truthy-wikipedia-issue` or the issue template.

The issue is a review queue, not a verdict and not an automated message to Wikipedia.

## Next pieces

The current scripts establish the trace and process boundaries. Later work can add:

- deterministic replay verification;
- an event-driven queue watcher using filesystem notifications rather than polling;
- source-type parsers for HTML, PDF, structured data, and media transcripts;
- browser capture for JavaScript-heavy pages;
- model comparison runners;
- a graph view of investigation branches;
- source ownership/provenance normalization;
- automatic claim extraction that still requires source pointers and preserves the raw model run.
