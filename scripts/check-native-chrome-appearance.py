#!/usr/bin/env python3
"""Exercise production AppKit chrome appearance and presentation lifetimes.

Compiles the actual surface implementation and Command-T material construction.
This checks state/focus/appearance propagation, not composited pixel contrast;
bright/dark background contrast still needs a headed browser inspection.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
args = parser.parse_args()
frame = (args.source / 'chrome/browser/ui/views/frame/browser_frame_view_mac.mm').read_text()
start = frame.index('@interface HeliumChromeHitRegion')
end = frame.index('// An overlay hairline', start)
surface = frame[start:end]
tint = frame[frame.index('NSColor* FloatingChromeTintColor('):frame.index('NSAppearance* FloatingChromeAppearance(')]
command = (args.source / 'chrome/browser/ui/helium/helium_command_bar_view_mac.mm').read_text()
start = command.index('  NSAppearance* appearance =')
end = command.index('\n}', start)
command_material = command[start:end]
policy = command_material.index("  const bool content_aware =")
material = command_material.index("  if (@available(macOS 26, *))", policy)
command_material = command_material[:policy] + command_material[material:]
colors = (args.source / 'chrome/browser/ui/views/helium/native_frame_materials_mac.mm').read_text()
start = colors.index('void SetNativeGlassControlAppearance(')
bridge = colors[start:colors.index('std::optional<SkColor> NativeGlassControlColor(', start)]
prefix = r'''
#import <AppKit/AppKit.h>
#import <QuartzCore/QuartzCore.h>
#import <objc/runtime.h>
#include <cassert>
#include <cstdio>
struct CommandNative { NSView* material = nil; };
NSView* MakeCommandMaterial(NSView* pane, bool dark, bool content_aware) {
  CommandNative native;
  CommandNative* native_ = &native;
'''
tint_prefix = r'''
using SkColor = uint32_t;
namespace ui { constexpr int kColorSysPrimary = 1; }
int SkColorGetR(SkColor c) { return (c >> 16) & 255; }
int SkColorGetG(SkColor c) { return (c >> 8) & 255; }
int SkColorGetB(SkColor c) { return c & 255; }
struct TestColorProvider {
  SkColor accent;
  SkColor GetColor(int id) const { assert(id == ui::kColorSysPrimary); return accent; }
};
struct BrowserView {
  TestColorProvider* colors = nullptr;
  const TestColorProvider* GetColorProvider() const { return colors; }
};
'''
bridge_prefix = r'''
char kGlassControlAppearanceKey;
namespace views {
struct NativeView { NSView* view; NSView* GetNativeNSView() { return view; } };
struct Widget {
 NSView* native = [[NSView alloc] init];
 int resets = 0, refreshes = 0;
 NativeView GetNativeView() { return {native}; }
 void ResetLastColorProviderKey() { ++resets; }
 void ScheduleThemeChanged() { ++refreshes; }
};
}
'''
fixture = r'''
@interface TestSurface : HeliumGlassSurface
- (NSView*)material;
- (NSView*)controls;
- (NSView*)effect;
- (NSView*)backdrop;
@end
@implementation TestSurface
- (NSView*)material { return _material; }
- (NSView*)controls { return _controls; }
- (NSView*)effect { return _effect; }
- (NSView*)backdrop { return _backdrop; }
@end
void DrainUntil(bool (^done)()) {
  NSDate* deadline = [NSDate dateWithTimeIntervalSinceNow:3];
  do {
    [NSRunLoop.currentRunLoop runMode:NSDefaultRunLoopMode
        beforeDate:[NSDate dateWithTimeIntervalSinceNow:.01]];
  } while (!done() && [deadline timeIntervalSinceNow] > 0);
  assert(done());
}
bool Dark(NSView* view) {
  return [[view.effectiveAppearance bestMatchFromAppearancesWithNames:
      @[NSAppearanceNameAqua, NSAppearanceNameDarkAqua]]
      isEqual:NSAppearanceNameDarkAqua];
}
int main() {
 @autoreleasepool {
  [NSApplication sharedApplication];
  // Startup theme notification before attachment must not dereference a
  // missing provider. Later calls use the owning browser's resolved palette.
  BrowserView browser;
  assert(FloatingChromeTintColor(&browser) == nil);
  TestColorProvider colors{0xff276c69};
  browser.colors = &colors;
  NSColor* light_tint = FloatingChromeTintColor(&browser);
  assert(fabs(light_tint.redComponent - 39.0/255) < .0001);
  assert(fabs(light_tint.greenComponent - 108.0/255) < .0001);
  assert(fabs(light_tint.blueComponent - 105.0/255) < .0001);
  assert(fabs(light_tint.alphaComponent - .30) < .0001);
  colors.accent = 0xff123456;
  NSColor* custom_tint = FloatingChromeTintColor(&browser);
  assert(fabs(custom_tint.redComponent - 18.0/255) < .0001);
  assert(fabs(custom_tint.greenComponent - 52.0/255) < .0001);
  assert(fabs(custom_tint.blueComponent - 86.0/255) < .0001);
  browser.colors = nullptr;
  assert(FloatingChromeTintColor(&browser) == nil);
  NSWindow* window = [[NSWindow alloc]
      initWithContentRect:NSMakeRect(0, 0, 600, 400)
      styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
  window.releasedWhenClosed = NO;
  TestSurface* surface = [[TestSurface alloc] initWithFrame:NSZeroRect];
  surface.frame = NSMakeRect(10, 10, 400, 36);
  [window.contentView addSubview:surface];
  NSView* material = surface.material;
  NSView* controls = surface.controls;
  assert([surface.effect isKindOfClass:NSGlassEffectView.class]);
  assert(!surface.backdrop.hidden);
  NSView* original_effect = surface.effect;
  assert(surface.hidden && !surface.isPresented && material.alphaValue == 0);
  NSTextField* field = [[NSTextField alloc] initWithFrame:NSMakeRect(30, 0, 280, 36)];
  field.stringValue = @"preserve editor contents";
  [controls addSubview:field];
  [surface setRevealFraction:.4];
  [window makeFirstResponder:field];
  NSResponder* responder = window.firstResponder;
  field.currentEditor.selectedRange = NSMakeRange(3, 5);
  assert(responder == field || field.currentEditor == responder);
  TestSurface* other = [[TestSurface alloc] initWithFrame:NSZeroRect];
  other.appearance = [NSAppearance appearanceNamed:NSAppearanceNameDarkAqua];
  for (NSAppearanceName name in @[NSAppearanceNameAqua, NSAppearanceNameDarkAqua,
      NSAppearanceNameAccessibilityHighContrastAqua,
      NSAppearanceNameAccessibilityHighContrastDarkAqua]) {
    surface.appearance = [NSAppearance appearanceNamed:name];
    bool dark = [name containsString:@"Dark"];
    for (NSColor* background in @[NSColor.whiteColor, NSColor.blackColor]) {
      window.backgroundColor = background;
      [surface layoutSubtreeIfNeeded];
      assert(surface.material == material && surface.controls == controls);
      assert(field.superview == controls && window.firstResponder == responder);
      assert([field.stringValue isEqual:@"preserve editor contents"]);
      assert(Dark(material) == dark && Dark(field) == dark);
      assert(Dark(other));
      assert(!surface.hidden && surface.isPresented && material.alphaValue == .4);
    }
  }
  for (int i = 0; i < 4; ++i) {
    // Theme changes must preserve the same live material, editor and selection,
    // including while switching fixed/adaptive mode.
    NSColor* tint = [(i % 2 ? NSColor.systemBlueColor : NSColor.systemGreenColor)
        colorWithAlphaComponent:.30];
    surface.themeTintColor = tint;
    surface.contentAware = i % 2 == 0;
    assert([((NSGlassEffectView*)surface.effect).tintColor isEqual:tint]);
    assert(other.themeTintColor == nil);
    assert(surface.controls == controls && field.superview == controls);
    assert(window.firstResponder == responder);
    assert(NSEqualRanges(field.currentEditor.selectedRange, NSMakeRange(3, 5)));
    assert([field.stringValue isEqual:@"preserve editor contents"]);
    assert(!surface.hidden && surface.isPresented && surface.material.alphaValue == .4);
    if (@available(macOS 26, *)) {
      assert(surface.material == material && surface.effect == original_effect);
      assert(surface.backdrop.hidden == surface.contentAware);
      assert(NSEqualRects(controls.frame, surface.bounds));
    }
  }
  material = surface.material;
  [surface setFrame:NSMakeRect(10, 10, 500, 36)];
  [surface layoutSubtreeIfNeeded];
  assert(NSEqualRects(material.frame, surface.bounds));
  assert(((NSGlassEffectView*)surface.effect).cornerRadius == 18);
  assert(surface.backdrop.layer.cornerRadius == 18);
  assert(NSEqualRects(controls.frame, surface.bounds));
  [surface setPresented:NO];
  surface.appearance = [NSAppearance appearanceNamed:NSAppearanceNameAqua];
  DrainUntil(^bool { return surface.hidden && material.alphaValue == 0; });
  assert(surface.hidden && !surface.isPresented && material.alphaValue == 0);
  [surface setPresented:YES];
  surface.appearance = [NSAppearance appearanceNamed:NSAppearanceNameDarkAqua];
  DrainUntil(^bool { return material.alphaValue == 1; });
  assert(!surface.hidden && surface.isPresented && material.alphaValue == 1);
  [surface setPresented:NO];
  [surface setPresented:YES];
  // Let the superseded hide completion run before checking visibility.
  NSDate* settled = [NSDate dateWithTimeIntervalSinceNow:.5];
  DrainUntil(^bool { return material.alphaValue == 1 &&
                            [settled timeIntervalSinceNow] <= 0; });
  assert(!surface.hidden && surface.isPresented && material.alphaValue == 1);
  HeliumSidebarSurface* sidebar = [[HeliumSidebarSurface alloc] initWithFrame:NSMakeRect(0,0,200,300)];
  assert(sidebar.materialCornerRadius == 0 && [sidebar hitTest:NSZeroPoint] == nil);
  for (int dark = 0; dark <= 1; ++dark) {
    for (int aware = 0; aware <= 1; ++aware) {
      NSView* pane = [[NSView alloc] initWithFrame:NSMakeRect(0,0,560,68)];
      NSView* popup = MakeCommandMaterial(pane, dark, aware);
      assert(popup.subviews.count == 2);
      NSView* backdrop = popup.subviews.firstObject;
      NSGlassEffectView* glass = (NSGlassEffectView*)popup.subviews.lastObject;
      assert([glass isKindOfClass:NSGlassEffectView.class]);
      assert(glass.contentView == pane && pane.appearance == nil);
      assert(glass.cornerRadius == 20 && backdrop.layer.cornerRadius == 20);
      assert(backdrop.hidden == bool(aware) && Dark(popup) == bool(dark));
    }
  }
  __block NSInteger notifications = 0;
  __block NSAppearance* foreground = nil;
  surface.onAppearanceChanged = ^(NSAppearance* appearance) {
    ++notifications;
    foreground = appearance;
  };
  surface.contentAware = YES;
  NSInteger before = notifications;
  surface.controls.appearance = [NSAppearance appearanceNamed:NSAppearanceNameAqua];
  surface.controls.appearance = [NSAppearance appearanceNamed:NSAppearanceNameDarkAqua];
  assert(notifications > before && [foreground.name isEqual:NSAppearanceNameDarkAqua]);
  surface.controls.appearance = nil;
  surface.contentAware = NO;
  assert(foreground == surface.controls.effectiveAppearance);
  views::Widget first, second;
  NSAppearance* dark = [NSAppearance appearanceNamed:NSAppearanceNameDarkAqua];
  SetNativeGlassControlAppearance(&first, dark);
  SetNativeGlassControlAppearance(&first, dark);
  assert(first.resets == 1 && first.refreshes == 1 && second.refreshes == 0);
  assert(objc_getAssociatedObject(first.native, &kGlassControlAppearanceKey) == dark);
  SetNativeGlassControlAppearance(&first, nil);
  assert(first.refreshes == 2 && !objc_getAssociatedObject(first.native, &kGlassControlAppearanceKey));
  [window close];
  puts("PASS: profile/high-contrast appearances, owner isolation, editor focus, reveal interruption, resize, persistent glass mode switching, sidebar, and Command-T material");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='lune-chrome-appearance-') as tmp:
    path = Path(tmp)
    (path / 'check.mm').write_text(prefix + command_material +
        '\nreturn native_->material;\n}\n' + tint_prefix + tint + surface + bridge_prefix + bridge + fixture)
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                    '-arch', args.arch, '-framework', 'AppKit',
                    '-framework', 'QuartzCore', str(path / 'check.mm'),
                    '-o', str(path / 'check')], check=True)
    subprocess.run(['/usr/bin/arch', '-' + args.arch, str(path / 'check')], check=True)
