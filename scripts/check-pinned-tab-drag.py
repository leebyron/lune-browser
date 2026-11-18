#!/usr/bin/env python3
"""Check pinned-grid insertion stability and active drop-placeholder policy."""
import argparse
from hashlib import file_digest
import json
from pathlib import Path
import platform
import subprocess
import tempfile


def block(text, marker):
    start = text.index(marker)
    brace = text.index('{', start)
    depth = 0
    for index in range(brace, len(text)):
        depth += (text[index] == '{') - (text[index] == '}')
        if depth == 0:
            return text[start:index + 1]
    raise ValueError(f'Unclosed production block: {marker}')


def sha(path):
    with path.open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    root = Path(__file__).resolve().parent.parent
    common = source / 'chrome/browser/ui/views/tabs/common'
    paint = block((common / 'dragged_tabs_container.cc').read_text(),
                  'void DraggedTabsContainer::PaintDropPlaceholder(')
    policy = block((common / 'pinned_tab_container_view.cc').read_text(),
                   'bool PinnedTabContainerView::HasEmptyDropEntry() const')
    empty = block((common / 'pinned_tab_container_view_vertical_layout.cc').read_text(),
                  'if (children_on_row == 0)')
    template = (root / 'tests/native/tab_drop_placeholder.cc').read_text()
    fixture = template.replace('// PRODUCTION_PAINT', paint).replace(
        '// PRODUCTION_EMPTY_LAYOUT', empty).replace(
        '// PRODUCTION_ENTRY_POLICY', policy)
    results = {}
    with tempfile.TemporaryDirectory(prefix='lune-pinned-tab-drag-') as temporary:
        scratch = Path(temporary)
        (scratch / 'placeholder.cc').write_text(fixture)
        for name, input_path in [
                ('grid', root / 'tests/native/pinned_tab_drop_target.cc'),
                ('placeholder', scratch / 'placeholder.cc')]:
            binary = scratch / name
            subprocess.run([
                '/usr/bin/xcrun', 'clang++', '-std=c++20', '-arch', args.arch,
                '-mmacosx-version-min=13.0', '-Wall', '-Wextra', '-Werror',
                '-I', str(source), str(input_path), '-o', str(binary)], check=True)
            identity = subprocess.check_output(['/usr/bin/file', str(binary)], text=True)
            if args.arch not in identity:
                raise RuntimeError(f'Wrong fixture architecture: {identity}')
            run = subprocess.run([str(binary)], capture_output=True, text=True, check=True)
            results[name] = run.stdout.strip()
    report = {
        'passed': True,
        'architecture': args.arch,
        'host_architecture': platform.machine(),
        'runtime': ('Rosetta on Apple silicon'
                    if args.arch == 'x86_64' and platform.machine() == 'arm64'
                    else 'native'),
        'checks': results,
        'production_sha256': {name: sha(common / name) for name in [
            'pinned_tab_drop_target.h', 'dragged_tabs_container.cc',
            'pinned_tab_container_view.cc', 'pinned_tab_container_view_vertical_layout.cc']},
        'scope': ('Grid tests call the production final-cell selector. Placeholder tests '
                  'compile production paint, entry-policy and empty-layout blocks with '
                  'lightweight Views/Canvas stubs; native pointer delivery is not simulated.'),
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
