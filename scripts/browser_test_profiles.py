"""Keep disposable browser profiles on internal storage, separate from evidence."""
import atexit
from pathlib import Path
import sys
import tempfile


_profiles = []


def temporary_profile(prefix='lune-test-profile-'):
    """Return a context-managed profile directory; ignore external TMPDIR on macOS."""
    if not prefix or Path(prefix).name != prefix or prefix in ('.', '..'):
        raise ValueError('Profile prefix must be a single filename component')
    # /private/tmp lives on the Mac's internal system/data storage. Do not use
    # the build-storage configuration or an inherited external TMPDIR here.
    directory = Path('/private/tmp') if sys.platform == 'darwin' else None
    return tempfile.TemporaryDirectory(prefix=prefix, dir=directory)


def new_profile(prefix='lune-test-profile-'):
    """Create a profile that survives browser restarts and is cleaned up at exit."""
    temporary = temporary_profile(prefix)
    _profiles.append(temporary)
    return Path(temporary.name)


def require_temporary_profile(profile):
    """Fail before browser startup if a release caller uses external evidence as a profile."""
    profile = Path(profile).resolve()
    if sys.platform == 'darwin' and not profile.is_relative_to('/private/tmp'):
        raise ValueError('Use new_profile() for an internal temporary browser profile')
    return profile


def cleanup_profiles():
    """Remove only profile directories created by this process."""
    while _profiles:
        _profiles.pop().cleanup()


atexit.register(cleanup_profiles)
