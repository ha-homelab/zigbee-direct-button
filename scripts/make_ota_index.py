#!/usr/bin/env python3
"""Create a narrowly matched z2m_local index beside a verified normal OTA image."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from check_ota import inspect_image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--url', required=True, help='Trusted public HTTPS artifact URL; no credentials')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    url = urlsplit(args.url)
    if url.scheme != 'https' or not url.netloc or url.username or url.password or url.query or url.fragment:
        parser.error('--url must be an HTTPS URL without credentials, query parameters, or fragments')
    if args.output.resolve().parent != args.image.resolve().parent:
        parser.error('Keep the index and image in the same directory')
    if args.output.exists():
        parser.error('Refusing to overwrite an existing index; review and replace it explicitly')
    try:
        metadata = inspect_image(args.image.read_bytes())
        entry = {key: metadata[key] for key in (
            'fileVersion', 'fileSize', 'imageType', 'manufacturerCode', 'sha512', 'otaHeaderString'
        )}
        entry.update({
            'fileName': args.image.name, 'path': args.image.name, 'url': args.url,
            'manufacturerName': ['mrpevh8p'], 'modelId': 'TS0041-TB',
            'releaseNotes': 'Experimental EndDevice 1.1.3-holdoff1; opt-in short-release Toggle and absolute Off on hold.',
        })
        with args.output.open('x') as output:
            output.write(json.dumps([entry], indent=2) + '\n')
    except (OSError, ValueError) as error:
        parser.exit(1, f'Cannot create index: {error}\n')
    print(f'Created {args.output.name}; deploy it with {args.image.name}')


if __name__ == '__main__':
    main()
