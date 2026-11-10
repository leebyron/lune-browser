#!/usr/bin/env python3
"""Exercise the production replacement traffic lights and widget close callback."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path)
parser.add_argument("--arch", choices=("arm64", "x86_64"), required=True)
args = parser.parse_args()
source = args.source.resolve()
controls = source / "chrome/browser/ui/views/helium/fullscreen_window_controls_mac"
header = controls.with_suffix(".h").read_text()
implementation = "\n".join(
    line for line in controls.with_suffix(".mm").read_text().splitlines()
    if not line.startswith(('#import "', '#include "'))
)
frame = (source / "chrome/browser/ui/views/frame/browser_frame_view_mac.mm").read_text()
start = frame.index("static void ConfigureWindowControlsCloseHandler(")
configure = frame[start:frame.index("// Reuse Helium's native traffic-light group", start)]
# Verify both host creation paths use the same tested callback wiring.
assert "ConfigureWindowControlsCloseHandler(helium_fullscreen_controls_, GetWidget());" in frame
assert "ConfigureWindowControlsCloseHandler(floating_window_controls_, GetWidget());" in frame

prefix = r'''
#import <AppKit/AppKit.h>
#import <objc/runtime.h>
#include <cassert>
#include <memory>
@interface BrowserNativeWidgetWindow : NSWindow
- (void)setAppKitFullscreenOverlaySuppressed:(BOOL)suppressed;
@end
@implementation BrowserNativeWidgetWindow
- (void)setAppKitFullscreenOverlaySuppressed:(BOOL)suppressed {}
@end
namespace base::apple {
template<typename T> T* ObjCCast(id object) {
 return [object isKindOfClass:[T class]] ? (T*)object : nil;
}
}
namespace views {
class Widget {
 public:
 enum class ClosedReason { kCloseButtonClicked };
 struct Weak {
  Widget* widget;
  std::weak_ptr<bool> alive;
  explicit operator bool() const { return !alive.expired(); }
  Widget* operator->() const { return widget; }
 };
 Weak GetWeakPtr() { return {this, alive}; }
 void CloseWithReason(ClosedReason reason) {
  assert(reason == ClosedReason::kCloseButtonClicked);
  ++requests;
 }
 int requests = 0;
 private:
 std::shared_ptr<bool> alive = std::make_shared<bool>(true);
};
}
@interface CloseDelegate : NSObject <NSWindowDelegate>
@property(nonatomic) int requests;
@end
@implementation CloseDelegate
- (BOOL)windowShouldClose:(id)sender { ++_requests; return NO; }
@end
'''
tests = r'''
BrowserNativeWidgetWindow* Window(bool closable = true) {
 auto style = NSWindowStyleMaskTitled | NSWindowStyleMaskResizable;
 if (closable) style |= NSWindowStyleMaskClosable;
 auto* w = [[BrowserNativeWidgetWindow alloc]
  initWithContentRect:NSMakeRect(0,0,700,450) styleMask:style
  backing:NSBackingStoreBuffered defer:NO];
 w.releasedWhenClosed = NO;
 return w;
}
NSButton* CloseButton(HeliumFullscreenWindowControls* controls) {
 for (NSButton* button in controls.subviews)
  if (button.action == NSSelectorFromString(@"closeWindow:")) return button;
 return nil;
}
int main() { @autoreleasepool {
 [NSApplication sharedApplication];
 auto* window = Window();
 auto* delegate = [CloseDelegate new]; window.delegate = delegate;
 auto* original = [window standardWindowButton:NSWindowCloseButton];
 original.hidden = YES; original.enabled = NO;
 [window performClose:nil]; assert(delegate.requests == 0);
 puts("PASS: reproduces AppKit refusing performClose with disabled original");
 auto* controls = [[HeliumFullscreenWindowControls alloc]
  initWithWindow:window size:NSMakeSize(82,36)];
 [window.contentView addSubview:controls];
 auto* button = CloseButton(controls); assert(button && button.enabled);
 views::Widget owner, other;
 ConfigureWindowControlsCloseHandler(controls, &owner);
 [button performClick:nil]; assert(owner.requests == 1 && other.requests == 0);
 assert(delegate.requests == 0 && original.hidden && !original.enabled);
 // The callback remains correct across original-button replacement/state changes.
 [controls hideTitlebarButtons]; [button performClick:nil];
 assert(owner.requests == 2 && original.hidden && !original.enabled);
 auto* second = [[HeliumFullscreenWindowControls alloc]
  initWithWindow:Window() size:NSMakeSize(82,36)];
 ConfigureWindowControlsCloseHandler(second, &other);
 [CloseButton(second) performClick:nil];
 assert(owner.requests == 2 && other.requests == 1);
 puts("PASS: owning widget, close reason, independent windows, native state preserved");
 auto dying = std::make_unique<views::Widget>();
 ConfigureWindowControlsCloseHandler(controls, dying.get());
 dying.reset(); [button performClick:nil];
 assert(owner.requests == 2);
 controls.closeHandler = nil; [button performClick:nil];
 __block HeliumFullscreenWindowControls* teardown =
  [[HeliumFullscreenWindowControls alloc] initWithWindow:Window() size:NSMakeSize(82,36)];
 __block int calls = 0;
 teardown.closeHandler = ^{ ++calls; teardown = nil; };
 [CloseButton(teardown) performClick:nil]; assert(calls == 1 && !teardown);
 puts("PASS: expired widget, missing callback, synchronous native-control teardown");
 auto* notClosable = [[HeliumFullscreenWindowControls alloc]
  initWithWindow:Window(false) size:NSMakeSize(82,36)];
 ConfigureWindowControlsCloseHandler(notClosable, &owner);
 assert(!CloseButton(notClosable).enabled);
 [CloseButton(notClosable) performClick:nil]; assert(owner.requests == 2);
 for (NSButton* b in controls.subviews) {
  if (b.action == @selector(performMiniaturize:)) assert(b.target == window && !b.enabled);
  if (b.action == @selector(toggleFullScreen:)) assert(b.target == window && b.enabled);
 }
 puts("PASS: nonclosable window and unchanged minimize/zoom targets");
} }
'''
with tempfile.TemporaryDirectory(prefix="lune-window-close-") as temp:
    path = Path(temp) / "close-test.mm"
    path.write_text("\n".join((prefix, header, implementation, configure, tests)))
    binary = path.with_suffix("")
    subprocess.run([
        "xcrun", "clang++", "-arch", args.arch, "-std=c++20", "-fobjc-arc",
        "-framework", "AppKit", str(path), "-o", str(binary),
    ], check=True)
    subprocess.run([str(binary)], check=True)
