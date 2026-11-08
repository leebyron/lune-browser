#!/usr/bin/env python3
"""Check the production sidebar button's activation lifecycle on macOS."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path, help="Prepared Chromium source tree")
parser.add_argument("--arch", choices=("arm64", "x86_64"))
args = parser.parse_args()
source = (args.source / "chrome/browser/ui/views/frame/browser_frame_view_mac.mm").read_text()
start = source.index("@interface HeliumSidebarPinButton : NSButton")
end = source.index("@interface HeliumGlassSidebarButton", start)
production = source[start:end]
prefix = r'''
#import <AppKit/AppKit.h>
#include <cassert>

@interface TestApplication : NSApplication
@property(nonatomic) BOOL fixtureActive;
@end
@implementation TestApplication
- (BOOL)isActive { return self.fixtureActive; }
@end

@interface TestWindow : NSWindow
@property(nonatomic) BOOL fixtureKey;
@end
@implementation TestWindow
- (BOOL)isKeyWindow { return self.fixtureKey; }
@end
'''
tests = r'''
@interface CountingPinButton : HeliumSidebarPinButton
@property(nonatomic) NSUInteger refreshCount;
@end
@implementation CountingPinButton
- (void)updateActivationTint {
  [super updateActivationTint];
  ++self.refreshCount;
}
@end

static void post(NSNotificationName name, id owner) {
  [NSNotificationCenter.defaultCenter postNotificationName:name object:owner];
}
static void expect(HeliumSidebarPinButton* button, BOOL active) {
  assert([button.contentTintColor isEqual:
      active ? NSColor.controlTextColor : NSColor.disabledControlTextColor]);
  assert(button.enabled);
}

int main() {
  @autoreleasepool {
    TestApplication* app = (TestApplication*)[TestApplication sharedApplication];
    app.fixtureActive = YES;
    TestWindow* a = [[TestWindow alloc] initWithContentRect:NSMakeRect(0, 0, 300, 200)
        styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
    TestWindow* b = [[TestWindow alloc] initWithContentRect:NSMakeRect(0, 0, 300, 200)
        styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
    a.fixtureKey = YES;
    b.fixtureKey = NO;
    __weak CountingPinButton* weakPin;
    @autoreleasepool {
    CountingPinButton* pin = [CountingPinButton
        buttonWithImage:[NSImage imageWithSystemSymbolName:@"sidebar.left"
                                 accessibilityDescription:nil]
        target:nil action:nil];
    assert([pin isKindOfClass:CountingPinButton.class]);
    [a.contentView addSubview:pin];
    expect(pin, YES);
    a.fixtureKey = NO;
    post(NSWindowDidResignKeyNotification, a);
    expect(pin, NO);
    a.fixtureKey = YES;
    post(NSWindowDidBecomeKeyNotification, a);
    expect(pin, YES);
    // App deactivation can occur while the window still reports itself key.
    app.fixtureActive = NO;
    post(NSApplicationDidResignActiveNotification, app);
    expect(pin, NO);
    app.fixtureActive = YES;
    post(NSApplicationDidBecomeActiveNotification, app);
    expect(pin, YES);
    NSUInteger count = pin.refreshCount;
    post(NSWindowDidBecomeKeyNotification, b);
    assert(pin.refreshCount == count);
    // Reparenting changes the owning window and unregisters the old one.
    [b.contentView addSubview:pin];
    expect(pin, NO);
    count = pin.refreshCount;
    post(NSWindowDidBecomeKeyNotification, a);
    assert(pin.refreshCount == count);
    b.fixtureKey = YES;
    post(NSWindowDidBecomeKeyNotification, b);
    expect(pin, YES);
    for (NSAppearanceName name in @[NSAppearanceNameAqua, NSAppearanceNameDarkAqua]) {
      pin.appearance = [NSAppearance appearanceNamed:name];
      expect(pin, YES);
      b.fixtureKey = NO;
      post(NSWindowDidResignKeyNotification, b);
      expect(pin, NO);
      b.fixtureKey = YES;
      post(NSWindowDidBecomeKeyNotification, b);
    }
    [pin removeFromSuperview];
    expect(pin, NO);
    count = pin.refreshCount;
    post(NSWindowDidBecomeKeyNotification, b);
    post(NSApplicationDidBecomeActiveNotification, app);
    assert(pin.refreshCount == count);
    weakPin = pin;
    pin = nil;
    }
    assert(!weakPin);
    post(NSWindowDidResignKeyNotification, b);
    puts("PASS: initial state, window/app activation, owner isolation, reparenting, appearance, enabled state, detach and teardown");
  }
}
'''
with tempfile.TemporaryDirectory(prefix="lune-sidebar-pin-") as temp:
    source_file = Path(temp) / "test.mm"
    source_file.write_text(prefix + production + tests)
    binary = source_file.with_suffix("")
    subprocess.run([
        "xcrun", "clang++", *(["-arch", args.arch] if args.arch else []),
        "-std=c++20", "-fobjc-arc", "-framework", "AppKit", str(source_file),
        "-o", str(binary),
    ], check=True)
    subprocess.run([str(binary)], check=True)
