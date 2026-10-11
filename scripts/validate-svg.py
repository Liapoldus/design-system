#!/usr/bin/env python3
"""Validate source SVGs and render them with librsvg for packaging checks."""
from pathlib import Path
import argparse
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG_NS = '{http://www.w3.org/2000/svg}'
XLINK_NS = '{http://www.w3.org/1999/xlink}'


def validate(path: Path, asset_root: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        return [f'{path}: invalid XML: {error}']
    if root.tag != f'{SVG_NS}svg':
        errors.append(f'{path}: root element is not SVG namespace <svg>')
    view_box = root.get('viewBox')
    if not view_box:
        errors.append(f'{path}: missing viewBox')
    else:
        try:
            values = [float(value) for value in view_box.replace(',', ' ').split()]
            if len(values) != 4 or values[2] <= 0 or values[3] <= 0:
                errors.append(f'{path}: invalid viewBox {view_box!r}')
        except ValueError:
            errors.append(f'{path}: invalid viewBox {view_box!r}')
    if root.find(f'{SVG_NS}title') is None:
        errors.append(f'{path}: missing accessible <title>')
    relative_parts = path.relative_to(asset_root).parts
    if relative_parts and relative_parts[0] == 'icons' and view_box != '0 0 24 24':
        errors.append(f'{path}: icon viewBox must be 0 0 24 24')
    for element in root.iter():
        if element.tag == f'{SVG_NS}image':
            errors.append(f'{path}: embedded or linked raster <image> is forbidden')
        for key in ('href', f'{XLINK_NS}href'):
            value = element.get(key)
            if value and not value.startswith('#'):
                errors.append(f'{path}: external resource reference {value!r} is forbidden')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true', help='Render each SVG to a temporary PNG with rsvg-convert')
    parser.add_argument('--package', action='store_true', help='Validate built distribution files in dist/')
    args = parser.parse_args()
    asset_root = ROOT / ('dist' if args.package else 'assets')
    paths = sorted(asset_root.rglob('*.svg'))
    errors = [error for path in paths for error in validate(path, asset_root)]
    if args.render and not errors:
        with tempfile.TemporaryDirectory(prefix='liapoldus-svg-check-') as directory:
            for index, path in enumerate(paths):
                output = Path(directory) / f'{index}.png'
                try:
                    subprocess.run(['rsvg-convert', '--width', '256', '--height', '256', str(path), '--output', str(output)], check=True, capture_output=True)
                except (FileNotFoundError, subprocess.CalledProcessError) as error:
                    detail = error.stderr.decode(errors='replace') if isinstance(error, subprocess.CalledProcessError) else str(error)
                    errors.append(f'{path}: librsvg rendering failed: {detail}')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Validated {len(paths)} SVG files' + (' and rendered all with librsvg' if args.render else ''))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
