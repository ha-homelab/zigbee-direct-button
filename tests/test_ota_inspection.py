"""Reject corrupted or mismatched deployment artifacts before offering an OTA."""
import binascii
import importlib.util
from pathlib import Path
import struct

import pytest

SPEC = importlib.util.spec_from_file_location('check_ota', Path(__file__).parents[1] / 'scripts/check_ota.py')
OTA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OTA)


def sample():
    payload = bytearray(64)
    payload[2:6] = (0x11033001).to_bytes(4, 'little')
    payload[6:8] = b'\x5d\x02'
    payload[8:12] = b'KNLT'
    payload[0x18:0x1c] = (68).to_bytes(4, 'little')
    payload += (binascii.crc32(payload) ^ 0xFFFFFFFF).to_bytes(4, 'little')
    header = OTA.HEADER.pack(0x0BEEF11E, 0x100, 56, 0, 4417, 45636, 0x11033001, 2, b'Test', 130)
    return header + OTA.SUBELEMENT.pack(0, len(payload)) + payload


def test_valid_image():
    info = OTA.inspect_image(sample())
    assert info['fileVersionHex'] == '0x11033001'
    assert info['telinkCrcValid'] is True
    assert info['fileSize'] == 130


@pytest.mark.parametrize('offset', [0, 4, 6, 8, 10, 12, 14, 52, 56, 58, 64, 68, 86, 100, 129])
def test_reject_corrupt_or_mismatched_image(offset):
    image = bytearray(sample())
    image[offset] ^= 1
    with pytest.raises(ValueError):
        OTA.inspect_image(image)


def test_reject_truncation():
    with pytest.raises(ValueError):
        OTA.inspect_image(sample()[:-1])


def test_reject_missing_boot_marker_even_with_valid_crc():
    image = bytearray(sample())
    image[70:74] = b"NONE"
    payload = image[62:-4]
    image[-4:] = (binascii.crc32(payload) ^ 0xFFFFFFFF).to_bytes(4, 'little')
    with pytest.raises(ValueError, match='boot marker'):
        OTA.inspect_image(image)


def test_reject_oversized_image_even_with_consistent_lengths_and_crc():
    image = bytearray(sample()[:-4])
    image += b"\0" * (0x34000 - len(image))
    payload_len = len(image) + 4 - 62
    image[52:56] = (len(image) + 4).to_bytes(4, 'little')
    image[58:62] = payload_len.to_bytes(4, 'little')
    image[86:90] = payload_len.to_bytes(4, 'little')
    image += (binascii.crc32(image[62:]) ^ 0xFFFFFFFF).to_bytes(4, 'little')
    with pytest.raises(ValueError, match='208 KiB'):
        OTA.inspect_image(image)
