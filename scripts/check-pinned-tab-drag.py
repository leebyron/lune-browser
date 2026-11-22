#!/usr/bin/env python3
"""Check pinned-grid insertion stability and active drop-placeholder policy."""
import argparse
from hashlib import file_digest
import json
from pathlib import Path
import platform
import re
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


def morph_fixture(source, common, template):
    tab = (common / 'tab_view.cc').read_text()
    layout = (common / 'tab_view_vertical_layout.cc').read_text()
    dragged = (common / 'dragged_tabs_container.cc').read_text()
    constants = (source / 'chrome/browser/ui/layout_constants.cc').read_text()
    tween = (source / 'ui/gfx/animation/tween.cc').read_text()
    sizes = '\n'.join(re.search(rf'case LayoutConstant::{name}:\s*return [^;]+;',
                                constants)[0]
                      for name in ('kVerticalTabHeight', 'kVerticalTabPinnedHeight'))
    bounds = block(dragged, 'void DraggedTabsContainer::OnViewBoundsChanged(')
    anchor = re.search(r'dragging_views_bounds_ = gfx::Rect\(([^;]+);', bounds)[0]
    assert 'ApplyLayout(CalculateLayout(TabView().width(), TabView().height()))' in layout
    assert 'animated_height.value_or(preferred_height)' in layout
    assert '0.5 * (container.height() - preferred_height)' in layout
    assert 'title_->layer()->SetOpacity(1.0 - GetPinDragProgress())' in tab
    assert 'RichAnimationDuration(base::Milliseconds(240))' in tab
    assert 'pin_drag_animation_.SetTweenType(gfx::Tween::EASE_IN_OUT)' in tab
    methods = '\n'.join(block(tab, marker) for marker in (
        'double TabView::GetPinDragTransitionProgress(',
        'gfx::Size TabView::GetPinDragSize(',
    ))
    return (template.replace('// PRODUCTION_ROW_HEIGHTS', sizes)
            .replace('// PRODUCTION_TWEEN', block(tween, 'int Tween::IntValueBetween('))
            .replace('// PRODUCTION_TRANSITION', methods)
            .replace('// PRODUCTION_FLOATING_BOUNDS', anchor))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--morph', action='store_true',
                        help='Check the taller tiles and proportional drag anchoring.')
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
        checks = [
                ('grid', root / 'tests/native/pinned_tab_drop_target.cc'),
                ('placeholder', scratch / 'placeholder.cc')]
        if args.morph:
            path = scratch / 'morph.cc'
            path.write_text(morph_fixture(
                source, common, (root / 'tests/native/pinned-tab-morph.cc').read_text()))
            checks.append(('morph', path))
        for name, input_path in checks:
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
    if args.morph:
        report['production_sha256'].update({
            name: sha(common / name)
            for name in ('tab_view.cc', 'tab_view_vertical_layout.cc')
        })
        report['scope'] += (' The morph fixture compiles the production height and'
                            ' anchor calculations with sampled animation progress.')
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
