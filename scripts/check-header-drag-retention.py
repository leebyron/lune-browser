#!/usr/bin/env python3
"""Check the production macOS header presentation decision during window drags."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
args = parser.parse_args()
frame = args.source / 'chrome/browser/ui/views/frame'
native = (frame / 'browser_frame_view_mac.mm').read_text()
start = native.index('void BrowserFrameViewMac::UpdateFloatingAddressBar()')
start = native.index('  const bool present =', start)
decision = native[start:native.index(';', start) + 1]

prefix = r'''
#import <Foundation/Foundation.h>
#include <cstdio>
@interface Header : NSObject
@property(nonatomic, getter=isPresented) BOOL presented;
@end
@implementation Header
@end
struct BrowserView {
  bool menu, pinned;
  bool IsTopChromeRevealHeldForMenu() const { return menu; }
  bool IsZenModeTopChromePinned() const { return pinned; }
};
bool Present(BrowserView* browser_view, Header* floating_address_bar_,
             bool customize_open, bool dragging, bool resizing,
             bool window_menu_open, bool in_rail, bool in_sidebar_header,
             bool within_retention, bool editing, bool bubble_open) {
'''
fixture = r'''
  return present;
}
int main() { @autoreleasepool {
  Header* header = [[Header alloc] init];
  for (unsigned mask = 0; mask < (1u << 12); ++mask) {
    auto bit = [mask](unsigned n) { return bool(mask & (1u << n)); };
    BrowserView browser{bit(0), bit(1)};
    const bool customize=bit(2), dragging=bit(3), resizing=bit(4), menu=bit(5);
    const bool previous=bit(6), rail=bit(7), sidebar=bit(8);
    const bool retention=bit(9), editing=bit(10), bubble=bit(11);
    header.presented = previous;
    const bool actual = Present(&browser, header, customize, dragging, resizing,
                               menu, rail, sidebar, retention, editing, bubble);
    bool expected;
    if (browser.menu || browser.pinned || customize)
      expected = true;
    else if (dragging || resizing || menu)
      expected = previous;
    else
      expected = rail || sidebar || retention || editing || (previous && bubble);
    if (actual != expected) {
      fprintf(stderr, "FAIL mask=%u: dragging=%d previous=%d actual=%d expected=%d\n",
              mask, dragging, previous, actual, expected);
      return 1;
    }
  }
  // Release resumes normal hover/collapse; no new persistent drag state exists.
  BrowserView browser{false, false};
  auto update = [&](bool dragging, bool rail) {
    header.presented = Present(&browser, header, false, dragging, false, false,
                               rail, false, false, false, false);
    return bool(header.presented);
  };
  header.presented = false;
  if (update(true, false) || update(true, true) || update(false, false) ||
      !update(false, true) || !update(true, false) || update(false, false))
    return 2;
  puts("PASS: 4096 production presentation states; hidden/visible drag retention, explicit reveals, resize/menu holds and release transitions");
} }
'''
with tempfile.TemporaryDirectory(prefix='lune-header-drag-') as temp:
    source = Path(temp) / 'fixture.mm'
    binary = Path(temp) / 'fixture'
    source.write_text(prefix + decision + fixture)
    subprocess.run(['/usr/bin/xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                    '-arch', args.arch, '-framework', 'Foundation',
                    str(source), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
