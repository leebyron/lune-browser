# Helium 0.22.2 adoption on Chromium 158

Lune integrates Helium core 0.22.2 and the corresponding 0.22.2.1 macOS
composition while retaining Chromium `158.0.8127.37`. The new core base
includes ungoogled-chromium `158.0.8127.36-1`. The Chromium archive pins are
the existing `.37` inputs on both architectures. The bundled uBlock Origin
input moves to `1.76.4`.

The composed platform retains both the upstream history and the Lune input
with native tab badges and hover cards at `8789aabfa8c2d08309e2ef8e5b906cd0b88ba0e8`.
It keeps the complete upstream patch series in order. The integration
preserves Lune's Spacious density, hidden-sidebar popover, native frame and
toolbar geometry, service defaults, product identity and PiP permission UI.
Persistence for pinned tabs remains disabled. Lune's regular pins and
pinned groups retain their existing behavior.

The new Downloads menu can copy a download link. Lune also cleans matching
tracking and campaign parameters from the first HTTP GET for a direct
download. The owner verified attachment navigation, HTML downloads, Save
Link As and the clipboard results on the arm64 review build.

The [investigation](2026-11-20-helium-chromium-159-investigation.md) records
the individual patch decisions and the initial Chromium 159 conflict audit.

## Validation

Fresh preparation applied all 667 patches with zero fuzz. The eight tab
status files matched an independent application of the exact patches from
main. The earlier accepted preview matched the rest of the prepared source
after normalizing only the case of `UTF-8` in the XML declarations of
1,309 translation and resource files. The
symlink inventories matched. The preparation log SHA-256 is
`f987a5fa0e8bac689f3553665091ee9c7a0ad0b3828f803c3173d0729bbea85d`.

Both builds passed packaged browser, ChromeDriver, Settings and internal
artwork smoke. The Apple silicon browser passed the first-request download,
link and clipboard checks with extensions disabled, plus the Setup default
and opt-out checks. It also passed seven headed PiP cases covering the
manual offer, Allow and Not Now, existing permissions and persistence.
The source fixtures for pinned-tab drag, sidebar activation, media controls
and the DevTools header passed on both architectures. Core and platform
patch lint, translation lint and manifest validation passed. The repository
suite ran 108 tests with 1 skipped.

| Target | Execution | Framework SHA-256 |
| --- | --- | --- |
| arm64 | Apple silicon | `8f08075cc759b1e3bd6d454f8907316b7b6e055dcaceddb5f8dd0411f3cd7b66` |
| x86_64 | Rosetta on Apple silicon | `fb3292c7813617844ba62f09b04b06603747518c715aa8df03e3ca6a93a0d929` |

Signed component inputs use `inputs/helium-0222-1/helium`
and `inputs/helium-0222-1/macos`. Detailed logs and
machine-readable results are under the investigation workspace's
`.work/input-audit/` directory.
