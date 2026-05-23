# spec-artifacts-app

## Commands

```bash
make test                     # run pytest
make lint                     # ruff + black check
make format                   # ruff + black format
make build                    # build package
make update-lock              # update poetry.lock
make add-package p=<name>     # add runtime dependency
make add-dev-package p=<name> # add dev dependency
make use-local p=<name>       # switch dep to local pypi.ix
make use-upstream p=<name>    # switch dep back to upstream
make local-publish            # publish to pypi.ix (local registry)
```