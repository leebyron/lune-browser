#!/usr/bin/env python3
"""Check native word navigation against production Chromium ICU and AppKit.

Run on an isolated prepared tree with both build configurations available and no
active build. Temporarily generate a small test graph in the selected output,
then restore its normal GN graph. Product source and GN arguments are unchanged.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
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
    gn = source / 'buildtools/mac/gn'
    siso = source / 'third_party/siso/cipd/siso'
    env = lune.build_env()
    helper = source / 'chrome/browser/ui/helium/native_word_navigation_mac.mm'
    assert helper.exists(), 'Word-navigation source is missing'
    for file in ('helium/helium_command_bar_view_mac.mm',
                 'views/frame/browser_frame_view_mac.mm'):
        text = (source / 'chrome/browser/ui' / file).read_text()
        assert 'helium::HandleNativeWordNavigation(control, textView,' in text, file
    arguments = (output / 'args.gn').read_bytes()
    log_path = report.with_suffix('.log')
    result = {'architecture': args.arch,
              'execution': ('Rosetta on Apple silicon' if args.arch == 'x86_64'
                            and platform.machine() == 'arm64' else 'native'),
              'source_sha256': hashlib.sha256(helper.read_bytes()).hexdigest(),
              'passed': False}
    try:
        with log_path.open('w') as log, tempfile.TemporaryDirectory(
                prefix='lune_word_check_', dir=source) as temporary:
            fixture = Path(temporary)
            shutil.copyfile(Path(__file__).resolve().parent.parent /
                            'tests/native/word_navigation_mac.mm', fixture / 'main.mm')
            (fixture / 'BUILD.gn').write_text('''executable("native_word_navigation_check") {
  testonly = true
  sources = [ "main.mm" ]
  deps = [
    "//base",
    "//base:i18n",
    "//chrome/browser/ui/helium:native_word_navigation",
  ]
  frameworks = [ "AppKit.framework" ]
}
''')
            label = f'//{fixture.name}:native_word_navigation_check'
            try:
                subprocess.run([str(gn), 'gen', str(output),
                                f'--root-target={label}', f'--root-pattern={label}'],
                               cwd=source, env=env, check=True,
                               stdout=log, stderr=subprocess.STDOUT)
                subprocess.run([str(siso), 'ninja', '--fast_local', '-C', str(output),
                                '-local_jobs=8', f'{fixture.name}:native_word_navigation_check'],
                               cwd=source, env=env, check=True,
                               stdout=log, stderr=subprocess.STDOUT)
                native = subprocess.run([str(output / 'native_word_navigation_check')],
                                        cwd=output, env=env, capture_output=True, text=True)
                log.write(native.stdout + native.stderr)
                log.flush()
                result.update(exit_code=native.returncode, output=native.stdout.strip())
                native.check_returncode()
                result['passed'] = True
            finally:
                assert (output / 'args.gn').read_bytes() == arguments
                subprocess.run([str(gn), 'gen', str(output)], cwd=source, env=env,
                               check=True, stdout=log, stderr=subprocess.STDOUT)
    except Exception as error:
        result.update(passed=False, error=str(error))
        raise
    finally:
        report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
