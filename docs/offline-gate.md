# The offline gate (NFR-001 metric 2)

This is a **manual** gate of this repository. No CI job runs it, and NFR-001
deliberately claims none: a job that claimed it would need to be specified
first, and specifying it is not part of agent-ix/spec-artifacts-app#3.

Run it once per release and record the result in the release notes.

## Why it exists

The manifest binds each artifact type to a schema by digest, and every `$ref` in
the emitted bundle is supposed to resolve from bytes the module or its pinned
toolchain already ships. If any of that quietly reached the network, a consumer
without network access would see a different module from the one this repository
tests — and the failure would only show up in their environment, not ours.

## Procedure

Populate the environment **with** the network, then take it away:

```bash
npm ci                # installs the pinned TypeSpec toolchain and semantic-core
poetry install        # installs the test dependencies
make dev-quire        # installs the Quire wheel (agent-ix/quire-rs#392)
```

Then run both gates with no network:

```bash
unshare --net --map-root-user make schemas-check
unshare --net --map-root-user make test
```

Both must exit 0.

## What a failure means

- `make schemas-check` failing offline means the TypeSpec projection reaches the
  network — most likely an unpinned dependency the lockfile did not capture.
- `make test` failing offline means a `$ref` in the emitted bundle, or a schema
  the suite loads, resolves against a remote `https://schemas.agent-ix.org/…`
  rather than against the committed bytes. FR-002-CON-2 is the constraint that
  forbids it, and the offline-`$ref` test in the schema-emission suite is what
  should have caught it first.

## Recording the run

Record, in the release notes for the version under test: the date, the machine
(Node version, Python version, CPU), and the two exit codes. Metric 4's 30 s
threshold is a bound on that same machine; a number without the machine beside
it is not a measurement.
