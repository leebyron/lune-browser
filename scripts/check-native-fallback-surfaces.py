#!/usr/bin/env python3
"""Compile production fallback surfaces on either architecture.

Selects the pre-26 construction paths in an isolated native fixture. This tests
geometry, input exclusion, appearance and shadow lifecycle on the host OS;
it does not claim to reproduce macOS 13's compositor or native window mask.
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
materials = (args.source / 'chrome/browser/ui/views/helium/native_frame_materials_mac.mm').read_text()
command = (args.source / 'chrome/browser/ui/helium/helium_command_bar_view_mac.mm').read_text()
edge = materials[materials.index('@interface HeliumFallbackSurfaceEdge'):materials.index('namespace helium {')]
helper = materials[materials.index('void AddNativeFallbackSurfaceEdge'):materials.index('namespace {', materials.index('void AddNativeFallbackSurfaceEdge'))]
surface = frame[frame.index('@interface HeliumChromeHitRegion'):frame.index('// An overlay hairline')]
surface = surface.replace('if (@available(macOS 26, *))', 'if (@available(macOS 99, *))')
command_class = command[command.index('@interface HeliumCommandMaterial'):command.index('@interface HeliumCommandResults')]
construct = command[command.index('  if (!native_->material) {'):command.index('\n}', command.index('  if (!native_->material) {'))]
constants = command[command.index('constexpr int kWidth'):command.index('int CommandBarHeight')]
radius_source = (args.source / 'chrome/browser/ui/views/helium/frame_corner_radius_mac.mm').read_text()
radius = radius_source[radius_source.index('int GetSystemWindowRadius()'):]
legacy_radius = radius.replace('GetSystemWindowRadius()', 'LegacyWindowRadius()').replace('macOS 26, *', 'macOS 99, *')
code = '''#import <AppKit/AppKit.h>
#import <QuartzCore/QuartzCore.h>
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include "chrome/browser/ui/helium/native_result_row_mac.h"
'''+radius+legacy_radius+constants+edge+'namespace helium {\n'+helper+'}\n'+surface+command_class+'''
@interface TestSurface : HeliumGlassSurface
- (NSView*)material;
- (NSView*)effect;
@end
@implementation TestSurface
- (NSView*)material { return _material; }
- (NSView*)effect { return _effect; }
@end
NSView* MakeCommand(NSView* pane, NSAppearance* appearance) {
 struct Native { NSView* material = nil; } native;
 auto* native_ = &native;
'''+construct+'''
 return native.material;
}
void CheckShadow(NSView* view) {
 assert(!view.clipsToBounds);
 assert(fabs(view.shadow.shadowColor.alphaComponent - .05) < .001);
 assert(view.shadow.shadowBlurRadius == 10);
 assert(view.shadow.shadowOffset.height == -3);
 assert(CGRectEqualToRect(CGPathGetBoundingBox(view.layer.shadowPath), view.bounds));
}
void CheckEdge(NSView* effect) {
 assert([effect isKindOfClass:NSVisualEffectView.class]);
 assert(effect.layer.masksToBounds);
 NSView* edge = effect.subviews.lastObject;
 assert([edge isKindOfClass:HeliumFallbackSurfaceEdge.class]);
 assert([edge hitTest:NSMakePoint(10, 10)] == nil);
 assert(NSEqualRects(edge.frame, effect.bounds));
 for (NSAppearanceName name in @[NSAppearanceNameAqua, NSAppearanceNameDarkAqua,
    NSAppearanceNameAccessibilityHighContrastAqua,
    NSAppearanceNameAccessibilityHighContrastDarkAqua]) {
  effect.appearance = [NSAppearance appearanceNamed:name];
  [edge viewDidChangeEffectiveAppearance];
  assert(edge.needsDisplay);
  NSBitmapImageRep* bitmap = [edge bitmapImageRepForCachingDisplayInRect:edge.bounds];
  [edge cacheDisplayInRect:edge.bounds toBitmapImageRep:bitmap];
  bool visible = false;
  for (NSInteger x = 0; x < bitmap.pixelsWide; ++x) {
   visible |= [bitmap colorAtX:x y:bitmap.pixelsHigh / 2].alphaComponent > 0;
  }
  assert(visible); // The hairline actually rasterizes; it is not just configured.
  assert([bitmap colorAtX:bitmap.pixelsWide / 2 y:bitmap.pixelsHigh / 2].alphaComponent == 0);
 }
}
int main() { @autoreleasepool {
 [NSApplication sharedApplication];
 assert(GetSystemWindowRadius() == 16);
 assert(LegacyWindowRadius() == 12);
 NSWindow* window = [[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,800,600)
    styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
 window.releasedWhenClosed = NO;
 TestSurface* surface = [[TestSurface alloc] initWithFrame:NSMakeRect(30,30,300,36)];
 [window.contentView addSubview:surface];
 [surface setRevealFraction:1];
 CheckShadow(surface.material);
 CheckEdge(surface.effect);
 [surface setFrameSize:NSMakeSize(480,200)];
 [surface resizeSubviewsWithOldSize:NSMakeSize(300,36)];
 CheckShadow(surface.material);
 CheckEdge(surface.effect);
 NSView* pane = [[NSView alloc] initWithFrame:NSMakeRect(48,48,600,52)];
 pane.autoresizingMask = NSViewWidthSizable | NSViewHeightSizable;
 NSView* command = MakeCommand(pane, [NSAppearance appearanceNamed:NSAppearanceNameAqua]);
 [window.contentView addSubview:command];
 CheckShadow(command);
 CheckEdge(command.subviews.lastObject);
 assert(NSEqualRects(pane.frame, command.bounds));
 for (NSValue* size in @[[NSValue valueWithSize:NSMakeSize(600,320)],
                         [NSValue valueWithSize:NSMakeSize(300,164)]]) {
  command.frameSize = size.sizeValue;
  [command layoutSubtreeIfNeeded];
  CheckShadow(command);
  CheckEdge(command.subviews.lastObject);
  assert(NSEqualRects(pane.frame, command.bounds));
 }
 [window close];
 puts("PASS: fallback hairlines rasterize in four appearances; content/hit bounds, resizing 5% control/Command-T shadows, and 16/12 pt frame branches");
}}
'''
with tempfile.TemporaryDirectory(prefix='lune-fallback-') as tmp:
    path = Path(tmp)
    (path / 'check.mm').write_text(code)
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                    '-mmacosx-version-min=13.0', '-I', str(args.source),
                    '-arch', args.arch, '-framework', 'AppKit', '-framework', 'QuartzCore',
                    str(path / 'check.mm'), '-o', str(path / 'check')], check=True)
    subprocess.run(['/usr/bin/arch', '-' + args.arch, str(path / 'check')], check=True)
