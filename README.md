# Lune

Lune is an open source Chromium browser for macOS, made by [Lee Byron](https://leebyron.com) for his own daily browsing. You can use it too.

- A vertical tab sidebar and toolbar that tuck away to give pages more room.
- Simplified, pinnable tab groups.
- A keyboard command menu: **Cmd-T** to search or switch tabs, **Cmd-/** to run browser commands.
- Automatic Older Tabs to keep inactive tabs out of the way.

Visit [lune.computer](https://lune.computer/) for a look at the browser.

## Download

- [Apple silicon](https://github.com/leebyron/lune-browser/releases/latest/download/Lune-macos-arm64.dmg)
- [Intel](https://github.com/leebyron/lune-browser/releases/latest/download/Lune-macos-x86_64.dmg)

[Release notes](https://github.com/leebyron/lune-browser/releases/latest).

## About this repository

- `main`: build configuration and tooling.
- [Website source](https://github.com/leebyron/lune-browser/tree/main/website).
- [component/helium](https://github.com/leebyron/lune-browser/tree/component/helium): core browser patches.
- [component/macos](https://github.com/leebyron/lune-browser/tree/component/macos): macOS patches and packaging.
- [Lockfile](https://github.com/leebyron/lune-browser/blob/main/manifests/browser.lock.json): exact build inputs.
- [Issues](https://github.com/leebyron/lune-browser/issues): bugs and suggestions.

## Credits

- [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium/): Chromium foundation.
- [Helium](https://helium.computer/): browser features.
- [Arc](https://arc.net/): interaction inspiration.

## License

- [GPL-3.0-or-later](LICENSE): Lune's original work.
- [NOTICE](NOTICE): third-party licenses and attribution.
