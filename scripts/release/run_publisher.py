#!/usr/bin/env python3
"""Launch publication with native utilities and the publisher's signing identity."""
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from lune import build_env


def publisher_env():
    env = build_env()
    # Compilation intentionally drops these. Publication needs the existing
    # Git signer and GitHub authentication, without inheriting the shell PATH.
    for name in ('GNUPGHOME', 'GPG_TTY', 'SSH_AUTH_SOCK',
                 'GH_TOKEN', 'GITHUB_TOKEN', 'GH_HOST', 'GH_CONFIG_DIR'):
        if name in os.environ:
            env[name] = os.environ[name]
    paths = ['/usr/bin', '/bin', '/usr/sbin', '/sbin']
    for tool in ('gh', 'gpg'):
        executable = shutil.which(tool)
        if not executable:
            raise ValueError(f'Publisher requires {tool} in the calling shell PATH')
        directory = str(Path(executable).resolve().parent)
        if directory not in paths:
            paths.append(directory)
    env['PATH'] = os.pathsep.join(paths)
    return env


def main():
    env = publisher_env()  # Fail before starting any publication operation.
    os.execve(sys.executable, [sys.executable, str(ROOT / 'scripts/release/publish.py'),
                              *sys.argv[1:]], env)


if __name__ == '__main__':
    main()
