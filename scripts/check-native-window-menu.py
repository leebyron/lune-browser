#!/usr/bin/env python3
"""Run native menu lifetime regression checks against a prepared Chromium tree.

Compiles the production controls implementation with minimal BrowserWindow and
ObjCCast stubs. The remote helper is an isolated fixture: no menu service is run.
Requires macOS and the configured Xcode toolchain.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source", type=Path, help="Prepared Chromium source tree")
parser.add_argument("--arch", choices=("arm64", "x86_64"))
args = parser.parse_args()
src = args.source.resolve()
controls = src / "chrome/browser/ui/views/helium/fullscreen_window_controls_mac"
header = controls.with_suffix(".h").read_text()
source = controls.with_suffix(".mm").read_text()
# Keep system imports; substitute only the Chromium dependencies above.
source = "\n".join(
    line for line in source.splitlines()
    if not line.startswith(('#import "', '#include "'))
)
prefix='''#import <AppKit/AppKit.h>
#import <objc/runtime.h>
#include <cassert>
@interface BrowserNativeWidgetWindow : NSWindow
- (void)setAppKitFullscreenOverlaySuppressed:(BOOL)suppressed;
@end
@implementation BrowserNativeWidgetWindow
- (void)setAppKitFullscreenOverlaySuppressed:(BOOL)suppressed {}
@end
namespace base::apple { template<typename T> T* ObjCCast(id object) { return [object isKindOfClass:[T class]] ? (T*)object : nil; } }
'''
tests='''
static void post(NSString* name,id object) { [NSNotificationCenter.defaultCenter postNotificationName:name object:object]; }
static NSButton* zoom(HeliumFullscreenWindowControls* controls) { for(NSButton* button in controls.subviews) if(button.action==@selector(toggleFullScreen:))return button;return nil; }
int main(){@autoreleasepool {
 [NSApplication sharedApplication];
 BrowserNativeWidgetWindow* window=[[BrowserNativeWidgetWindow alloc] initWithContentRect:NSMakeRect(0,0,700,450) styleMask:NSWindowStyleMaskTitled|NSWindowStyleMaskResizable backing:NSBackingStoreBuffered defer:NO];
 HeliumFullscreenWindowControls* a=[[HeliumFullscreenWindowControls alloc] initWithWindow:window size:NSMakeSize(80,36)];
 HeliumFullscreenWindowControls* b=[[HeliumFullscreenWindowControls alloc] initWithWindow:window size:NSMakeSize(80,36)];
 [window.contentView addSubview:a];[window.contentView addSubview:b];
 assert(!a.windowManagementMenuOpen && !b.windowManagementMenuOpen);
 NSMenu* menu=[[NSMenu alloc] initWithTitle:@"Test"];
 menu.delegate=(id<NSMenuDelegate>)zoom(a).cell;
 NSMenu* other=[[NSMenu alloc] initWithTitle:@"Other"];
 other.delegate=(id<NSMenuDelegate>)zoom(b).cell;
 post(NSMenuDidBeginTrackingNotification,menu);
 assert(a.windowManagementMenuOpen && !b.windowManagementMenuOpen);
 post(NSMenuDidBeginTrackingNotification,other);
 assert(a.windowManagementMenuOpen && b.windowManagementMenuOpen);
 post(NSMenuDidEndTrackingNotification,other);
 assert(a.windowManagementMenuOpen && !b.windowManagementMenuOpen);
 post(NSMenuDidEndTrackingNotification,menu);
 assert(!a.windowManagementMenuOpen);
 // An unrelated child or menu cannot retain controls.
 NSView* child=[[NSView alloc] initWithFrame:NSZeroRect];[zoom(a) addSubview:child];
 assert(!a.windowManagementMenuOpen);[child removeFromSuperview];
 NSMenu* unrelated=[[NSMenu alloc] initWithTitle:@"Unrelated"];
 post(NSMenuDidBeginTrackingNotification,unrelated);assert(!a.windowManagementMenuOpen);
 // The actual remote-view type is recognizable through its public view tree.
 Class remoteClass=NSClassFromString(@"NSThemeWidgetZoomMenuRemoteView");
 assert(remoteClass);
 NSView* remote=[[remoteClass alloc] initWithFrame:NSZeroRect];
 [zoom(a) addSubview:remote];
 // Cached/prepared helper with no running menu must not retain the sidebar.
 assert(!a.windowManagementMenuOpen && !b.windowManagementMenuOpen);
 Ivar running=class_getInstanceVariable(remoteClass,"_runningMenu");assert(running);
 auto* runningFlag=(unsigned char*)(__bridge void*)remote+ivar_getOffset(running);
 // Model AppKit opening and closing without removing its cached helper.
 *runningFlag=1;assert(a.windowManagementMenuOpen && !b.windowManagementMenuOpen);
 *runningFlag=0;assert(!a.windowManagementMenuOpen && !b.windowManagementMenuOpen);
 *runningFlag=1;assert(a.windowManagementMenuOpen);
 *runningFlag=0;
 [remote removeFromSuperview];assert(!a.windowManagementMenuOpen);
 // Detachment releases notification retention.
 post(NSMenuDidBeginTrackingNotification,menu);assert(a.windowManagementMenuOpen);
 [a removeFromSuperview];assert(!a.windowManagementMenuOpen);
 a=nil;post(NSMenuDidEndTrackingNotification,menu);
 puts("PASS: owning-control identity, independent menus, unrelated end/children, cached remote helper, running/closed/running cycles, remote-view detach, detach and observer teardown");
}}
'''
with tempfile.TemporaryDirectory(prefix="lune-native-menu-") as temp:
    source_file = Path(temp) / "controls-test.mm"
    source_file.write_text(prefix + header + source + tests)
    binary = source_file.with_suffix("")
    subprocess.run([
        "xcrun", "clang++", *(["-arch", args.arch] if args.arch else []),
        "-std=c++20", "-fobjc-arc", "-framework", "AppKit",
        str(source_file), "-o", str(binary),
    ], check=True)
    subprocess.run([str(binary)], check=True)
