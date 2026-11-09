# Native toolbar modes

These fixtures exercise the production macOS toolbar modes without any Lune
launch flags. They preserve the issue #11 pixel/input and preference regression
coverage, with the removed independent panel-position control omitted from UI
assertions (the opposite-side preference invariant is still checked).

Run with an output directory containing Lune.app and chromedriver, and a fresh
evidence directory. The renderer fixture requires Pillow:

```
python3 check.py /path/to/output /path/to/fresh-evidence --toggle
python3 check-settings.py /path/to/output /path/to/fresh-settings-evidence
```

The renderer checks cover 52 pt protective insets, viewport-fit cover/contain,
safe-area values, root/body background painting, scroll-under pixels, nested
scrolling, hit alignment, live mode changes, background tabs, default preferences,
and restart persistence. Settings checks cover all three modes, both sidebar
sides, backend synchronization, opposite panel placement, and persistence.
Native visual acceptance and native Intel hardware remain separate checks.
