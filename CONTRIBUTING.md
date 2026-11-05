# Contributing

Keep changes narrow and preserve the behavior of existing binding modes. Add a command-contract test when changing press timing, long-press behavior, state persistence, or Zigbee output. Run `make stub/build stub/build_end_device` and `python3 -m pytest tests/ -q` before proposing changes.

The firmware source is based on a pinned upstream project. Prefer changes that can be explained as a small delta; retain provenance and license text. Update the focused patch and `PROVENANCE.json` when rebasing. Do not claim a board is supported based solely on a shared retail name.

Runtime integration must remain scoped to hardware/firmware that implements its advertised controls. In particular, do not expose mode 4 globally to devices running unpatched firmware. The example quirk is intentionally narrower than the inherited development generator.

Document host tests, artifact validation, actual installed version, and physical acceptance as separate evidence. CI cannot prove a radio update or a light turning off. Read `SECURITY.md` before sharing logs or deployment details.


Use GitHub issues for non-sensitive bugs and enhancements, and pull requests for changes. English reports are welcome. Read [governance](GOVERNANCE.md), [conduct](CODE_OF_CONDUCT.md), and the [roadmap](ROADMAP.md). Preserve the upstream permissive grant and separate third-party licenses when contributing; do not import incompatible code.

Follow the existing C formatting (`uncrustify.cfg`) and Python PEP 8 naming/indentation. Use bounded inputs and explicit failure paths. New functionality requires positive/negative tests; fixes require a regression that exercises the affected behavior. For shared C changes, also build with `HOST_CC=clang SANITIZERS=address,undefined` and run tests with `UBSAN_OPTIONS=halt_on_error=1`. Run `python -m ruff check --isolated --ignore-noqa --select E9,F63,F7,F82 .` for common Python mistakes. These basic diagnostics do not enforce every style rule.

Resolve substantive review findings and required CI before normal merge. Target-specific source changes additionally require the actual target build before a firmware release; host tests do not authorize flashing hardware. The focused `patches/hold-off.patch` remains the original feature delta; later maintenance/security changes are recorded in Git history and CHANGELOG.md.

## Hashed Python dependencies

`requirements.txt` declares the direct tooling versions. CI, the development
container, and `make setup_venv` install the complete `requirements.lock` with artifact
hashes. Regenerate with uv 0.13.4 when a direct version
changes, then run the host and packaged-runtime checks:

```sh
uv pip compile requirements.txt .github/requirements-wheels-only.in --python-version=3.12 --universal --generate-hashes --output-file=requirements.lock
```

Python 3.12 CI requires binary wheels. PyYAML 6.0.3 has no Python 3.15 wheel,
so the container and local setup build only that verified source archive using
the separately hashed setuptools/Cython backend, with build isolation disabled.
All other packages still require wheels. Regenerate the backend lock with:

```sh
uv pip compile requirements-build.in .github/requirements-wheels-only.in --python-version=3.12 --universal --generate-hashes --output-file=requirements-build.lock
```

The dependency-lock test rejects direct inputs that no longer match either lock.
The packaged-runtime CI job compiles and tests under the actual Python 3.15 image.
