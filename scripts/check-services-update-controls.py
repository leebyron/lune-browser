#!/usr/bin/env python3
"""Exercise production Helium update gates and migration with isolated prefs."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def function(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    services = source / 'components/helium_services'
    helpers = (services / 'helium_services_helpers.cc').read_text()
    schema = (services / 'schema.cc').read_text()
    prefs = (source / 'chrome/browser/prefs/browser_prefs.cc').read_text()
    registration = (source / 'chrome/browser/ui/browser_ui_prefs.cc').read_text()
    start = registration.index('    registry->RegisterIntegerPref(prefs::kHeliumSchemaVersion')
    registration = registration[start:registration.index('\n  }', start)]
    migration = function(prefs, '  if (!profile_prefs->GetUserPrefValue(prefs::kHeliumComponentUpdatesEnabled))')
    functions = '\n'.join([
        function(helpers, 'bool ShouldAccessServices('),
        function(schema, 'bool HasAcceptedSchema('),
        function(schema, 'void AcceptCurrentSchema('),
        function(schema, 'bool ShouldShowSchemaNotification('),
        function(helpers, 'bool ShouldAccessUpdateService('),
        function(helpers, 'bool ShouldAccessComponentUpdateService('),
    ])
    version = re.search(r'inline constexpr int kHeliumCurrentSchemaVersion = \d+;',
                        (services / 'schema.h').read_text()).group(0)
    harness = r'''
#include <cassert>
#include <map>
#include <string>
#include "components/helium_services/pref_names.h"
struct PrefService {
  std::map<std::string, int> defaults, user;
  int GetInteger(const char* key) const {
    auto it = user.find(key);
    return it == user.end() ? defaults.at(key) : it->second;
  }
  bool GetBoolean(const char* key) const { return GetInteger(key); }
  void SetInteger(const char* key, int value) { user[key] = value; }
  void SetBoolean(const char* key, bool value) { user[key] = value; }
  const int* GetUserPrefValue(const char* key) const {
    auto it = user.find(key);
    return it == user.end() ? nullptr : &it->second;
  }
  void RegisterIntegerPref(const char* key, int value) { defaults[key] = value; }
  void RegisterBooleanPref(const char* key, bool value) { defaults[key] = value; }
  void RegisterStringPref(const char*, const char*) {}
};
void Register(PrefService* registry) {
REGISTRATION
}
void Migrate(PrefService* profile_prefs) {
MIGRATION
}
namespace helium {
VERSION
FUNCTIONS
}
int main() {
  using namespace prefs;
  // The complete update/consent matrix: the browser toggle must never grant
  // component access, and optional service consent must never gate the browser.
  for (bool browser : {false, true})
  for (bool component : {false, true})
  for (bool enabled : {false, true})
  for (bool consented : {false, true})
  for (bool accepted : {false, true}) {
    PrefService p; Register(&p);
    p.SetBoolean(kHeliumUpdateFetchingEnabled, browser);
    p.SetBoolean(kHeliumComponentUpdatesEnabled, component);
    p.SetBoolean(kHeliumServicesEnabled, enabled);
    p.SetBoolean(kHeliumServicesConsented, consented);
    if (accepted) helium::AcceptCurrentSchema(p);
    assert(helium::ShouldAccessUpdateService(p) == browser);
    assert(helium::ShouldAccessComponentUpdateService(p) ==
           (component && enabled && consented && accepted));
    const bool notify = enabled && consented && !accepted;
    assert(helium::ShouldShowSchemaNotification(p) == notify);
    p.SetInteger(kHeliumDismissedSchemaVersion, helium::kHeliumCurrentSchemaVersion);
    assert(!helium::ShouldShowSchemaNotification(p));
    assert(helium::HasAcceptedSchema(p, helium::kHeliumCurrentSchemaVersion) == accepted);
    assert(helium::ShouldAccessComponentUpdateService(p) ==
           (component && enabled && consented && accepted));
    // Dismissal of an older version must not suppress a newer notice.
    p.SetInteger(kHeliumDismissedSchemaVersion, helium::kHeliumCurrentSchemaVersion - 1);
    assert(helium::ShouldShowSchemaNotification(p) == notify);
    p.SetBoolean(kHeliumDisableSchemaAlerts, true);
    assert(!helium::ShouldShowSchemaNotification(p));
  }
  // Migration preserves both old values, including the default. Once split,
  // changing browser updates and relaunching cannot overwrite the service choice.
  for (bool old : {false, true}) {
    PrefService p; Register(&p);
    p.SetBoolean(kHeliumUpdateFetchingEnabled, old);
    Migrate(&p);
    assert(p.GetBoolean(kHeliumComponentUpdatesEnabled) == old);
    p.SetBoolean(kHeliumUpdateFetchingEnabled, !old);
    Migrate(&p);
    assert(p.GetBoolean(kHeliumComponentUpdatesEnabled) == old);
    p.SetBoolean(kHeliumComponentUpdatesEnabled, !old);
    Migrate(&p);
    assert(p.GetBoolean(kHeliumComponentUpdatesEnabled) == !old);
  }
  PrefService p; Register(&p); Migrate(&p);
  assert(p.GetBoolean(kHeliumComponentUpdatesEnabled));
  p.SetBoolean(kHeliumUpdateFetchingEnabled, false); Migrate(&p);
  assert(p.GetBoolean(kHeliumComponentUpdatesEnabled));
}
'''
    for marker, value in [('REGISTRATION', registration), ('MIGRATION', migration),
                          ('VERSION', version), ('FUNCTIONS', functions)]:
        harness = harness.replace(marker, value)
    with tempfile.TemporaryDirectory(prefix='lune-services-controls-') as directory:
        path = Path(directory)
        (path / 'check.cc').write_text(harness)
        subprocess.run(['/usr/bin/xcrun', 'clang++', '-std=c++20', '-arch', args.arch,
                        '-I', str(source), str(path / 'check.cc'), '-o', str(path / 'check')],
                       check=True)
        subprocess.run([str(path / 'check')], check=True)
    print(f'PASS ({args.arch}): production update/consent matrix, dismissal, and one-time migration')


if __name__ == '__main__':
    main()
