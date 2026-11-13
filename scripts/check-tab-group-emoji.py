#!/usr/bin/env python3
"""Check production group emoji parsing and raster bounds with Chromium ICU/Skia.

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
    args = parser.parse_args()
    source = args.source.resolve()
    report = args.report.resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    output = source / 'out' / ('Default' if args.arch == 'arm64' else 'Intel')
    text = (source / 'chrome/browser/ui/views/tabs/common/tab_group_header_view.cc').read_text()
    helpers = (re.search(r'constexpr int kIconSize = \d+;', text).group() + '\n' +
               text[text.index('constexpr int kEmojiFontSize'):
                    text.index('\nviews::ScrollView* GetScrollView')])
    fixture_template = (Path(__file__).resolve().parent.parent /
                        'tests/native/tab_group_emoji.cc').read_text()
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
                prefix='lune_group_emoji_check_', dir=source) as temporary:
            fixture = Path(temporary)
            (fixture / 'main.cc').write_text(
                fixture_template.replace('// PRODUCTION_HELPERS', helpers))
            (fixture / 'BUILD.gn').write_text('''executable("tab_group_emoji_check") {
  testonly = true
  sources = [ "main.cc" ]
  deps = [ "//base", "//base:i18n", "//ui/gfx", "//skia" ]
}
''')
            label = f'//{fixture.name}:tab_group_emoji_check'
            try:
                subprocess.run([str(gn), 'gen', str(output),
                                f'--root-target={label}', f'--root-pattern={label}'],
                               cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT,
                               check=True)
                subprocess.run([str(source / 'third_party/siso/cipd/siso'), 'ninja',
                                '--fast_local', '-C', str(output), '-local_jobs=8',
                                f'{fixture.name}:tab_group_emoji_check'],
                               cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT,
                               check=True)
                run = subprocess.run([str(output / 'tab_group_emoji_check')], cwd=output,
                                     env=env, capture_output=True, text=True)
                log.write(run.stdout + run.stderr)
                result.update(exit_code=run.returncode, output=run.stdout.strip())
                run.check_returncode()
                result['passed'] = True
            finally:
                assert (output / 'args.gn').read_bytes() == arguments
                subprocess.run([str(gn), 'gen', str(output)], cwd=source, env=env,
                               stdout=log, stderr=subprocess.STDOUT, check=True)
    finally:
        report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
