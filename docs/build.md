# Build, inspect, and trace an image

## Host tests

Python 3.12 and a C compiler are sufficient for the host simulation. From this repository:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
make stub/build stub/build_end_device
python3 -m pytest tests/ -q
```

Run only the new behavior contract during development:

```sh
python3 -m pytest tests/test_garage_hold_off.py -q
```

These tests run two host-native simulation variants, not a physical radio. They verify no early action, short-release Toggle, exactly one long Off, no dimming/late Toggle, repeated holds, settings surviving a simulated restart, no commands while unjoined, and no spurious action when releasing a key held during boot. Nineteen additional artifact tests reject corrupt or mismatched OTA files.

## Firmware build

The TC32 compiler runs on Linux x86_64. Docker on an Apple Silicon Mac needs amd64 emulation for **both build and run**:

```sh
docker build --platform linux/amd64 -t zigbee-direct-button .
mkdir -p output
docker run --rm --platform linux/amd64 \
  -v "$PWD/output:/output" zigbee-direct-button
```

On an existing Linux x86_64 build machine, install the packages listed in `Dockerfile`, create the Python environment above, then run `bash scripts/build.sh`. The script uses the checked-in source, rather than fetching an unreviewed branch.

Outputs:

- `ts0041-hold-off-1.1.3.1.bin`: raw compiled application, for inspection or a separately planned wired recovery procedure.
- `ts0041-hold-off-1.1.3.1.zigbee`: normal OTA image for the already-converted target.
- `metadata.json`: checked OTA identity, lengths, CRC, and hashes.
- `SHA256SUMS`: hashes of the two artifacts.

The OTA identity is manufacturer **4417 / 0x1141**, image type **45636 / 0xb244**, file version **0x11033001**, label **1.1.3-holdoff1**. The version is newer than the upstream `0x11033000` target. The image is **not** a stock conversion image.

```sh
python3 scripts/check_ota.py output/ts0041-hold-off-1.1.3.1.zigbee
(cd output && sha256sum -c SHA256SUMS)
```

The inspector rejects mismatched identity, inconsistent lengths, a mismatched embedded version, and an incorrect boot marker, oversized image, or incorrect Telink CRC. This checks the artifact structure; it does not prove hardware compatibility or authenticity. Obtain artifacts from a trusted release and compare its published hash before installation.

## Dependencies and reproducibility

`PROVENANCE.json` pins the upstream source commit and records the target. `patches/hold-off.patch` is the focused behavior/test delta against that source. The checked-in source directories preserve this patched upstream snapshot; the target-only runtime quirk is a separate deployment wrapper.

The upstream download recipe uses Telink SDK **3.7.2.0** and verifies the TC32 compiler archive against SHA-256:

```text
33b854be3e3db3dba4b4dacdda2cd4ea1c94dfd4d562864a095956de7991b430
```

The SDK is selected by its upstream release tag. The SDK archive hash, Docker base digest, and OS package versions are not fully pinned here. Therefore this is a repeatable recipe, not a claim of bit-for-bit reproducibility. Record the output metadata and resolved build environment with each release; investigate differences rather than substituting binaries silently.

Do not use broad `make setup` or a default Router build for this button. `scripts/build.sh` supplies the exact EndDevice target, pin map, OTA identity, and version. Downloaded SDK/toolchains remain outside version control.
