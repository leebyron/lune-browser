#!/usr/bin/env python3
"""Render the shared address/Command-T result button with native AppKit.

Check selection pixels, appearance invalidation, resizing, and button dispatch.
Autocomplete/provider behavior requires separate browser interaction checks.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
args = parser.parse_args()
row_source = args.source / 'chrome/browser/ui/helium/native_result_row_mac.mm'
fixture = r'''
@interface Target : NSObject
@property NSInteger acceptedTag;
- (void)accept:(NSButton*)sender;
@end
@implementation Target
- (void)accept:(NSButton*)sender { self.acceptedTag = sender.tag; }
@end
NSBitmapImageRep* Render(NSView* view) {
  NSBitmapImageRep* bitmap = [view bitmapImageRepForCachingDisplayInRect:view.bounds];
  [view cacheDisplayInRect:view.bounds toBitmapImageRep:bitmap];
  return bitmap;
}
CGFloat Alpha(NSBitmapImageRep* bitmap, NSInteger x, NSInteger y) {
  return [bitmap colorAtX:x y:y].alphaComponent;
}
NSRect InkBounds(NSBitmapImageRep* bitmap) {
  NSInteger left = bitmap.pixelsWide, top = bitmap.pixelsHigh, right = -1, bottom = -1;
  for (NSInteger y = 0; y < bitmap.pixelsHigh; ++y) {
    for (NSInteger x = 0; x < bitmap.pixelsWide; ++x) {
      if (Alpha(bitmap, x, y) > .1) {
        left = std::min(left, x); right = std::max(right, x);
        top = std::min(top, y); bottom = std::max(bottom, y);
      }
    }
  }
  return NSMakeRect(left, top, right - left + 1, bottom - top + 1);
}
int main() {
 @autoreleasepool {
  [NSApplication sharedApplication];
  Target* target = [[Target alloc] init];
  HeliumNativeResultRow* row = [HeliumNativeResultRow
      buttonWithTitle:@"" target:target action:@selector(accept:)];
  assert([row isKindOfClass:HeliumNativeResultRow.class]);
  row.bordered = NO;
  row.contentTintColor = NSColor.labelColor;
  row.autoresizingMask = NSViewWidthSizable;
  row.tag = 4;
  assert(!row.acceptsFirstResponder);
  [row updateTrackingAreas];
  assert(row.trackingAreas.count == 0);
  __block NSInteger hovered = -1;
  row.onHover = ^(NSInteger index) { hovered = index; };
  [row updateTrackingAreas];
  assert(row.trackingAreas.count == 1);
  [row mouseEntered:[NSEvent otherEventWithType:NSEventTypeApplicationDefined
      location:NSZeroPoint modifierFlags:0 timestamp:0 windowNumber:0
      context:nil subtype:0 data1:0 data2:0]];
  assert(hovered == 4);
  row.onHover = nil;
  [row updateTrackingAreas];
  assert(row.trackingAreas.count == 0);
  row.frame = NSMakeRect(0, 0, 320, 52);
  NSWindow* window = [[NSWindow alloc]
      initWithContentRect:NSMakeRect(0, 0, 720, 40)
                styleMask:NSWindowStyleMaskBorderless
                  backing:NSBackingStoreBuffered defer:NO];
  window.releasedWhenClosed = NO;
  [window.contentView addSubview:row];
  [window orderFront:nil];
  for (NSString* name in @[NSAppearanceNameAqua, NSAppearanceNameDarkAqua,
                          NSAppearanceNameAccessibilityHighContrastAqua,
                          NSAppearanceNameAccessibilityHighContrastDarkAqua]) {
    row.appearance = [NSAppearance appearanceNamed:name];
    row.needsDisplay = NO;
    [row viewDidChangeEffectiveAppearance];
    assert(row.needsDisplay);
    for (NSNumber* width in @[@80, @320, @700]) {
      row.frame = NSMakeRect(0, 0, width.doubleValue, 52);
      row.selected = NO;
      NSBitmapImageRep* empty = Render(row);
      assert(Alpha(empty, empty.pixelsWide / 2, empty.pixelsHigh / 2) < .01);
      row.needsDisplay = NO;
      row.selected = YES;
      assert(row.needsDisplay);
      NSBitmapImageRep* selected = Render(row);
      CGFloat alpha = Alpha(selected, selected.pixelsWide / 2, selected.pixelsHigh / 2);
      assert(alpha > .20 && alpha < .30);
      assert(Alpha(selected, 0, 0) < .01);
      assert(Alpha(selected, selected.pixelsWide - 1, selected.pixelsHigh - 1) < .01);
      row.selected = NO;
      NSBitmapImageRep* cleared = Render(row);
      assert(Alpha(cleared, cleared.pixelsWide / 2, cleared.pixelsHigh / 2) < .01);
    }
  }
  // Compare SF glyph bounds with AppKit's unscaled image view, independently
  // of the row's icon-slot layout. A 16-point symbol is not a 16x16 bitmap.
  row.frame = NSMakeRect(0, 0, 320, 52);
  NSImageView* reference = [[NSImageView alloc] initWithFrame:NSMakeRect(0, 0, 40, 52)];
  reference.imageScaling = NSImageScaleNone;
  [window.contentView addSubview:reference];
  for (NSString* symbol in @[@"magnifyingglass", @"globe"]) {
    NSImage* image = [[NSImage imageWithSystemSymbolName:symbol accessibilityDescription:nil]
        imageWithSymbolConfiguration:[NSImageSymbolConfiguration
            configurationWithPointSize:16 weight:NSFontWeightMedium]];
    row.symbolName = symbol;
    reference.image = [image imageWithSymbolConfiguration:[NSImageSymbolConfiguration
        configurationWithHierarchicalColor:NSColor.labelColor]];
    NSRect actual = InkBounds(Render(row));
    NSRect native = InkBounds(Render(reference));
    assert(std::abs(actual.size.width - native.size.width) <= 1);
    assert(std::abs(actual.size.height - native.size.height) <= 1);
  }
  // A rectangular downloaded icon keeps its aspect ratio inside the favicon slot.
  NSImage* favicon = [NSImage imageWithSize:NSMakeSize(32, 16) flipped:NO
      drawingHandler:^BOOL(NSRect rect) { [NSColor.blackColor setFill]; NSRectFill(rect); return YES; }];
  row.resultImage = favicon;
  NSBitmapImageRep* faviconBitmap = Render(row);
  NSRect faviconBounds = InkBounds(faviconBitmap);
  CGFloat backingScale = faviconBitmap.pixelsWide / 320.0;
  assert(std::abs(faviconBounds.size.width / backingScale - 16) <= 1);
  assert(std::abs(faviconBounds.size.height / backingScale - 8) <= 1);
  assert([@"Switch to Tab" sizeWithAttributes:@{NSFontAttributeName :
      [NSFont systemFontOfSize:11]}].width <= 82);
  [reference removeFromSuperview];
  row.resultImage = nil;
  row.symbolName = nil;
  // A normal native button retains its action and index without taking focus
  // or introducing a separate mouse-tracking implementation.
  [row performClick:nil];
  assert(target.acceptedTag == 4);
  row.primaryText = @"A long address suggestion that truncates at a narrow width";
  row.secondaryText = @"https://example.test/a/long/path";
  row.tagText = @"History";
  row.symbolName = @"globe";
  row.lineBreakMode = NSLineBreakByTruncatingTail;
  row.alignment = NSTextAlignmentLeft;
  row.font = [NSFont systemFontOfSize:13];
  row.frame = NSMakeRect(12, 4, 80, 52);
  row.selected = YES;
  Render(row);
  NSView* parent = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, 104, 40)];
  [parent addSubview:row];
  parent.frame = NSMakeRect(0, 0, 344, 40);
  assert(row.frame.size.width == 320 && row.frame.size.height == 52);
  [window close];
  puts("PASS: selection fill/clear, rounded bounds, light/dark/high-contrast redraw, narrow/wide resize, truncation, native SF sizing, favicon aspect, action label fit, target/action/tag");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='lune-address-suggestions-') as tmp:
    path = Path(tmp)
    (path / 'check.mm').write_text('#import \"chrome/browser/ui/helium/native_result_row_mac.h\"\n#include <algorithm>\n#include <cmath>\n#include <cassert>\n#include <cstdio>\n' + fixture)
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                    '-arch', args.arch, '-framework', 'AppKit',
                    '-I', str(args.source.resolve()), str(row_source), str(path / 'check.mm'), '-o', str(path / 'check')], check=True)
    subprocess.run(['/usr/bin/arch', '-' + args.arch, str(path / 'check')], check=True)
