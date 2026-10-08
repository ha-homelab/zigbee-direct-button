# Contributing

Keep changes narrow and preserve the behavior of existing binding modes. Add a command-contract test when changing press timing, long-press behavior, state persistence, or Zigbee output. Run `make stub/build stub/build_end_device` and `python3 -m pytest tests/ -q` before proposing changes.

The firmware source is based on a pinned upstream project. Prefer changes that can be explained as a small delta; retain provenance and license text. Update the focused patch and `PROVENANCE.json` when rebasing. Do not claim a board is supported based solely on a shared retail name.

Runtime integration must remain scoped to hardware/firmware that implements its advertised controls. In particular, do not expose mode 4 globally to devices running unpatched firmware. The example quirk is intentionally narrower than the inherited development generator.

Document host tests, artifact validation, actual installed version, and physical acceptance as separate evidence. CI cannot prove a radio update or a light turning off. Read `SECURITY.md` before sharing logs or deployment details.
