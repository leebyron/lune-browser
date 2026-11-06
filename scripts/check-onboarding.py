#!/usr/bin/env python3
"""Exercise the actual onboarding generator with and without an XML declaration."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def check(tree):
    source = tree / 'components/helium_onboarding'
    node = tree / 'third_party/node/mac_arm64/node-darwin-arm64/bin/node'
    original = (source / 'helium_onboarding_strings.grdp').read_text()
    plain = re.sub(r'^\s*<\?xml[^?]*\?>\s*', '', original)
    variants = [plain, '<?xml version="1.0" encoding="utf-8"?>\n' + plain]
    outputs = []
    with tempfile.TemporaryDirectory(prefix='lune-onboarding-') as tmp:
        fixture = Path(tmp)
        shutil.copytree(source / 'util', fixture / 'util')
        (fixture / 'node_modules').symlink_to((source / 'node_modules').resolve())
        (fixture / 'src/lib').mkdir(parents=True)
        for text in variants:
            (fixture / 'helium_onboarding_strings.grdp').write_text(text)
            header = fixture / 'localized_strings.h'
            subprocess.run([node.resolve(), fixture / 'util/generate-i18n.mts', header], check=True)
            result = (header.read_text(), (fixture / 'src/lib/strings.ts').read_text())
            messages = ET.fromstring(text).findall('message')
            if not messages or any(message.attrib['name'] not in result[0] for message in messages):
                raise AssertionError('Generated header does not cover every onboarding message.')
            outputs.append(result)
    if outputs[0] != outputs[1]:
        raise AssertionError('XML declaration changes generated onboarding strings.')
    print(f'Onboarding generator passed: {len(messages)} messages; identical header and TypeScript with/without XML declaration.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_tree', type=Path)
    check(parser.parse_args().source_tree.resolve())
