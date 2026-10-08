#!/usr/bin/env python3
"""Validate this project's normal-update OTA artifact using only the stdlib."""
import argparse
import binascii
import hashlib
import json
from pathlib import Path
import struct

HEADER = struct.Struct('<I5HIH32sI')
SUBELEMENT = struct.Struct('<HI')
EXPECTED = (4417, 45636, 0x11033001)


def inspect_image(data: bytes) -> dict:
    if len(data) > 0x40000:
        raise ValueError('OTA image exceeds the target 256 KiB limit')
    if len(data) < HEADER.size + SUBELEMENT.size + 32:
        raise ValueError('Truncated OTA image')
    magic, revision, header_len, fields, manufacturer, image_type, version, stack, label, size = HEADER.unpack_from(data)
    if magic != 0x0BEEF11E or revision != 0x100:
        raise ValueError('Unsupported Zigbee OTA identifier/header revision')
    if header_len != HEADER.size or fields != 0:
        raise ValueError('Expected the fixed header without optional fields')
    if size != len(data):
        raise ValueError('OTA total length does not match the file')
    if (manufacturer, image_type, version) != EXPECTED:
        raise ValueError('Not the expected TS0041-TB hold-off normal-update image')
    tag, payload_len = SUBELEMENT.unpack_from(data, header_len)
    payload = data[header_len + SUBELEMENT.size:]
    if tag != 0 or payload_len != len(payload):
        raise ValueError('Expected one complete firmware payload')
    if payload[8:12] != b'KNLT':
        raise ValueError('Missing Telink boot marker')
    if payload[6:8] != b'\x5d\x02':
        raise ValueError('Missing Telink OTA marker')
    if int.from_bytes(payload[2:6], 'little') != version:
        raise ValueError('Embedded firmware version differs from OTA version')
    if int.from_bytes(payload[0x18:0x1c], 'little') != len(payload):
        raise ValueError('Embedded Telink length differs from payload size')
    crc = binascii.crc32(payload[:-4]) ^ 0xFFFFFFFF
    if int.from_bytes(payload[-4:], 'little') != crc:
        raise ValueError('Telink firmware CRC mismatch')
    return {
        'manufacturerCode': manufacturer, 'imageType': image_type,
        'fileVersion': version, 'fileVersionHex': f'0x{version:08x}',
        'fileSize': len(data), 'payloadSize': payload_len,
        'otaHeaderString': label.rstrip(b'\x00').decode('ascii'),
        'zigbeeStackVersion': stack, 'telinkCrcValid': True,
        'sha256': hashlib.sha256(data).hexdigest(),
        'sha512': hashlib.sha512(data).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    args = parser.parse_args()
    try:
        metadata = inspect_image(args.image.read_bytes())
    except (OSError, ValueError, UnicodeDecodeError) as error:
        parser.exit(1, f'Invalid image: {error}\n')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
