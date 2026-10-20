#!/usr/bin/env bash
# Build the checked-in source. This script does not contact Home Assistant or flash hardware.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
OUTPUT_DIR=${OUTPUT_DIR:-"$ROOT/output"}
if [[ $(uname -s) != Linux || $(uname -m) != x86_64 ]]; then
  echo "The Telink compiler needs Linux x86_64. Use the documented amd64 container." >&2
  exit 1
fi
cd "$ROOT"
mkdir -p "$OUTPUT_DIR"
make stub/build stub/build_end_device
python3 -m pytest tests/ -q
make -C src/telink -f tools.mk sdk toolchain
# Compiler defines are not dependency-tracked upstream; discard stale objects.
rm -rf -- "$ROOT/build/telink"
make -C src/telink build ota \
  DEVICE_TYPE=end_device \
  'CONFIG_STR=mrpevh8p;TS0041-TB;BB4d;SB5u;ID2;BTB5;M;' \
  VERSION_STR=1.1.3-holdoff2 FILE_VERSION=0x11033002 \
  NVM_MIGRATIONS_VERSION=1 IMAGE_TYPE=45636 OTA_IMAGE_TYPE=45636 \
  FIRMWARE_BASENAME=ts0041-hold-off-1.1.3.2
cp build/telink/bin/ts0041-hold-off-1.1.3.2.bin "$OUTPUT_DIR/"
cp build/telink/bin/ts0041-hold-off-1.1.3.2.ota "$OUTPUT_DIR/ts0041-hold-off-1.1.3.2.zigbee"
python3 scripts/check_ota.py "$OUTPUT_DIR/ts0041-hold-off-1.1.3.2.zigbee" > "$OUTPUT_DIR/metadata.json"
(cd "$OUTPUT_DIR" && sha256sum ts0041-hold-off-1.1.3.2.bin ts0041-hold-off-1.1.3.2.zigbee > SHA256SUMS)
cat "$OUTPUT_DIR/metadata.json"
