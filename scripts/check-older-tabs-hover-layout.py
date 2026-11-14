#!/usr/bin/env python3
"""Check the production Older Tabs hover footer with real Views layout.

Use a prepared source with the requested architecture already built and no active
build in that output. The temporary test graph is restored before returning.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import tempfile

import lune


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--bubble-source', type=Path)
    parser.add_argument('--expect-failure', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve()
    report = args.report.resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    output = source / 'out' / ('Default' if args.arch == 'arm64' else 'Intel')
    production = (source / 'chrome/browser/ui/views/tabs/hovercard/tab_hover_card_bubble_view.cc').read_text()
    text = args.bubble_source.read_text() if args.bubble_source else production
    start = text.index('    // FadeView measures') if '    // FadeView measures' in text else text.index('    last_used_label_ = AddChildView(')
    construction = text[start:text.index('    // Set up layout.', start)]
    spacing_start = production.index('    // Share one outer inset')
    spacing_end = production.index('    auto short_time', spacing_start)
    spacing = production[spacing_start:spacing_end]
    footer = (source / 'chrome/browser/ui/views/tabs/hovercard/fade_footer_view.cc').read_text()
    constants = '\n'.join(re.findall(r'constexpr (?:auto kFooterMargins|int kFooterRowSpacing|int kIconLabelSpacing) = [^;]+;', footer))
    layout_start = footer.index('  flex_layout_ =', footer.index('FooterView::FooterView()'))
    layout = footer[layout_start:footer.index('  alert_row_ =', layout_start)]
    opening = footer.index('{', footer.index('FooterRow<T>::FooterRow('))
    depth, end = 1, opening + 1
    while depth:
        depth += (footer[end] == '{') - (footer[end] == '}')
        end += 1
    memory_row = footer[opening + 1:end - 1]
    helpers = '\n'.join([construction, spacing, constants, layout, memory_row])
    fixture_template = (Path(__file__).resolve().parent.parent /
                        'tests/native/older_tabs_hover_layout.cc').read_text()
    gn = source / 'buildtools/mac/gn'
    env = lune.build_env()
    arguments = (output / 'args.gn').read_bytes()
    result = {'architecture': args.arch,
              'execution': ('Rosetta on Apple silicon' if args.arch == 'x86_64'
                            and platform.machine() == 'arm64' else 'native'),
              'production_helpers_sha256': hashlib.sha256(helpers.encode()).hexdigest(),
              'passed': False}
    try:
        with report.with_suffix('.log').open('w') as log, tempfile.TemporaryDirectory(
                prefix='lune_older_hover_layout_check_', dir=source) as temporary:
            fixture = Path(temporary)
            (fixture / 'main.cc').write_text(
                fixture_template.replace('// PRODUCTION_FOOTER\n', construction).replace('// PRODUCTION_SPACING', spacing).replace('// PRODUCTION_FOOTER_CONSTANTS', constants).replace('// PRODUCTION_EXISTING_LAYOUT', layout).replace('// PRODUCTION_MEMORY_ROW', memory_row))
            (fixture / 'BUILD.gn').write_text('''executable("older_tabs_hover_layout_check") {
  testonly = true
  sources = [ "main.cc", "//chrome/browser/ui/views/tabs/hovercard/fade_label_view.cc", "//chrome/browser/ui/views/tabs/hovercard/filename_elider.cc" ]
  deps = [ "//base", "//base:i18n", "//ui/views", "//ui/base", "//ui/gfx", "//skia", "//components/color:color_headers" ]
}
''')
            label = f'//{fixture.name}:older_tabs_hover_layout_check'
            try:
                subprocess.run([str(gn), 'gen', str(output),
                                f'--root-target={label}', f'--root-pattern={label}'],
                               cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT,
                               check=True)
                subprocess.run([str(source / 'third_party/siso/cipd/siso'), 'ninja',
                                '--fast_local', '-C', str(output), '-local_jobs=8',
                                f'{fixture.name}:older_tabs_hover_layout_check'],
                               cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT,
                               check=True)
                pak = output / 'Lune.app/Contents/Frameworks/Lune Framework.framework/Resources/en.lproj/locale.pak'
                run = subprocess.run([str(output / 'older_tabs_hover_layout_check'), str(pak)], cwd=output,
                                     env=env, capture_output=True, text=True)
                log.write(run.stdout + run.stderr)
                result.update(exit_code=run.returncode, output=(run.stdout + run.stderr).strip())
                result['expected_regression'] = args.expect_failure
                result['passed'] = run.returncode == (1 if args.expect_failure else 0)
                if not result['passed']:
                    raise RuntimeError(result['output'])
            finally:
                assert (output / 'args.gn').read_bytes() == arguments
                subprocess.run([str(gn), 'gen', str(output)], cwd=source, env=env,
                               stdout=log, stderr=subprocess.STDOUT, check=True)
    finally:
        report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
