#!/usr/bin/env bash
# Experimental Telink commissioning image. Building does not authorize flashing.
# Establish the physical processor and the stock OTA identity before installation.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
OUTPUT_DIR=${OUTPUT_DIR:-"$ROOT/output/zg101zs-probe"}
if [[ $(uname -s) != Linux || $(uname -m) != x86_64 ]]; then
  echo "Use the documented Linux amd64 build container." >&2
  exit 1
fi
cd "$ROOT"
mkdir -p "$OUTPUT_DIR"
make -C src/telink -f tools.mk sdk toolchain
# The upstream Makefile does not track changes to compiler defines.
rm -rf -- "$ROOT/build/telink"
make -C src/telink build ota \
  DEVICE_TYPE=end_device \
  'CONFIG_STR=wkai4ga5;TS0044-ZG101-PROBE;' \
  VERSION_STR=1.1.3-zg101-probe FILE_VERSION=0x11033002 \
  NVM_MIGRATIONS_VERSION=1 IMAGE_TYPE=61696 OTA_IMAGE_TYPE=61696 \
  FIRMWARE_BASENAME=zg101zs-probe-1.1.3.2
cp build/telink/bin/zg101zs-probe-1.1.3.2.bin "$OUTPUT_DIR/"
cp build/telink/bin/zg101zs-probe-1.1.3.2.ota "$OUTPUT_DIR/zg101zs-probe-1.1.3.2.zigbee"
python3 - "$OUTPUT_DIR" <<'PY'
import json
import pathlib
import sys

sys.path.insert(0, 'scripts')
import check_ota

# Keep the TS0041 validator's public default and deployment path unchanged.
check_ota.EXPECTED = (4417, 61696, 0x11033002)
root = pathlib.Path(sys.argv[1])
image = root / 'zg101zs-probe-1.1.3.2.zigbee'
metadata = check_ota.inspect_image(image.read_bytes())
metadata.update(
    profile='experimental-no-gpio',
    manufacturer='wkai4ga5',
    model='TS0044-ZG101-PROBE',
    device_type='end_device',
    hardware_compatibility_verified=False,
    stock_conversion_image=False,
)
(root / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(json.dumps(metadata, indent=2))
PY
(cd "$OUTPUT_DIR" && sha256sum zg101zs-probe-1.1.3.2.bin zg101zs-probe-1.1.3.2.zigbee > SHA256SUMS)
