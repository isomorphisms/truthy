# Model workers

Truthy deliberately does not own a model API. A worker is any process with this contract:

```text
stdin   prompt/input
stdout  proposed analysis
stderr  diagnostics
status  0 on success, nonzero on failure
```

The runner records a human-readable model id and an exact revision label supplied by the caller, along with prompt/output hashes and exact argv.

Initial comparison candidates are Qwen, GPT-OSS, and Pythia. Do not treat the family name as a pinned model. Record the exact checkpoint/revision when a worker is wired up.

Pythia training and checkpoint experiments remain owned by `fuego-ironworks/gym`; Truthy should call that work through a worker adapter rather than duplicate training ownership here. Large weight blobs should not be silently committed to ordinary Truthy Git history. Adapter code, revision manifests, prompts, outputs, and investigation traces belong here; model weights can remain in the model store used by the worker.

Running multiple workers on the same frozen evidence is useful because disagreement is itself a retrieval signal. It is not a vote that manufactures truth.
