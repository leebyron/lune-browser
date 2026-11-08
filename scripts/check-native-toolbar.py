#!/usr/bin/env python3
"""Check the floating toolbar's AppKit symbol and semantic-color contracts."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'))
args = parser.parse_args()
root = args.source / 'chrome/browser/ui/views/helium'
source = (root / 'native_frame_materials_mac.mm').read_text()
header = (root / 'native_frame_materials.h').read_text()
start = header.index('enum class NativeGlassColorRole')
enum = header[start:header.index('};', start) + 2]
start = source.index('    switch (role) {')
end = source.index('    NSColor* color =', start)
selector = 'NSColor* SelectColor(NativeGlassColorRole role) {\nNSColor* semantic=NSColor.labelColor;\n' + source[start:end] + 'return semantic;\n}\n'
start = source.index('gfx::ImageSkia NativeToolbarSymbol(')
end = source.index('\n}  // namespace helium', start)
symbol = source[start:end]
# Stand-ins isolate the AppKit calls from Chromium's Views and Skia runtime.
# Actual image masking, input and layout are checked in the browser preview.
prefix = r'''
#import <AppKit/AppKit.h>
#include <algorithm>
#include <cassert>
#include <string_view>
#include <initializer_list>
using SkColor = unsigned;
namespace views { struct View { bool floating; }; }
bool IsFloatingToolbarControl(const views::View* view) { return view->floating; }
namespace gfx {
using ImageSkia = NSImage*;
NSImage* ImageSkiaFromNSImage(NSImage* image) { return image; }
struct ImageSkiaOperations {
 static NSImage* CreateColorMask(NSImage* image, SkColor) { return image; }
};
}
'''
tests = r'''
int main() {
 @autoreleasepool {
  [NSApplication sharedApplication];
  assert([NSImage imageWithSystemSymbolName:@"slider.horizontal.below.rectangle"
      accessibilityDescription:nil]);
  views::View view{true};
  for (auto name : {"kMoreVertIcon", "kChromeExtensionIcon", "kDownloadIcon",
                    "kPrintIcon", "kHistoryIcon", "kTranslateIcon", "kShareIcon",
                    "kSplitSceneIcon", "kSplitSceneOldIcon", "kHotelClassIcon",
                    "kDeleteIcon", "kCastIcon", "kQrCodeIcon", "kCodeIcon",
                    "kTableChartIcon", "kLinkIcon", "kEditIcon", "kAccountBoxIcon",
                    "kQueueMusicIcon", "kAccountCircleIcon", "kManageSearchIcon",
                    "kTabSearchTabStripOldIcon", "kIncognitoIcon",
                    "kIncognitoRefreshMenuOldIcon"}) {
   NSImage* image=NativeToolbarSymbol(&view,name,20,0);
   assert(image && NSEqualSizes(image.size,NSMakeSize(20,20)));
   for (int scale : {1, 2}) {
    const int pixels = 20 * scale;
    NSBitmapImageRep* bitmap = [[NSBitmapImageRep alloc]
        initWithBitmapDataPlanes:nil pixelsWide:pixels pixelsHigh:pixels
        bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO
        colorSpaceName:NSCalibratedRGBColorSpace bytesPerRow:0 bitsPerPixel:0];
    [NSGraphicsContext saveGraphicsState];
    NSGraphicsContext.currentContext =
        [NSGraphicsContext graphicsContextWithBitmapImageRep:bitmap];
    NSAffineTransform* transform = [NSAffineTransform transform];
    [transform scaleBy:scale];
    NSImageRep* rep = [image bestRepresentationForRect:NSMakeRect(0,0,20,20)
        context:nil hints:@{NSImageHintCTM:transform}];
    [rep drawInRect:NSMakeRect(0,0,pixels,pixels) fromRect:NSZeroRect
        operation:NSCompositingOperationCopy fraction:1 respectFlipped:NO
        hints:nil];
    [NSGraphicsContext restoreGraphicsState];
    int count=0, left=pixels, right=0, bottom=pixels, top=0;
    for (int y=0;y<pixels;++y) for (int x=0;x<pixels;++x) {
     if ([bitmap colorAtX:x y:y].alphaComponent > .1) {
      ++count; left=std::min(left,x); right=std::max(right,x);
      bottom=std::min(bottom,y); top=std::max(top,y);
     }
    }
    printf("%s @%dx pixels=%d bounds=%d,%d-%d,%d\n",name,scale,count,left,bottom,right,top);
    assert(count > 4 * scale * scale);
   }
  }
  assert(!NativeToolbarSymbol(&view,"unrecognized-extension-artwork",20,0));
  assert(!NativeToolbarSymbol(&view,"kChromeExtensionOffIcon",20,0));
  view.floating=false;
  assert(!NativeToolbarSymbol(&view,"kMoreVertIcon",20,0));
  for (NSAppearanceName name in @[NSAppearanceNameAqua,NSAppearanceNameDarkAqua]) {
   [[NSAppearance appearanceNamed:name] performAsCurrentDrawingAppearance:^{
    NSColor* normal=[SelectColor(NativeGlassColorRole::kToolbarLabel)
        colorUsingColorSpace:NSColorSpace.sRGBColorSpace];
    NSColor* hover=[SelectColor(NativeGlassColorRole::kToolbarHover)
        colorUsingColorSpace:NSColorSpace.sRGBColorSpace];
    NSColor* pressed=[SelectColor(NativeGlassColorRole::kToolbarPressed)
        colorUsingColorSpace:NSColorSpace.sRGBColorSpace];
    NSColor* disabled=[SelectColor(NativeGlassColorRole::kDisabledLabel)
        colorUsingColorSpace:NSColorSpace.sRGBColorSpace];
    assert(normal.alphaComponent > 0 && normal.alphaComponent < 1);
    assert(![normal isEqual:hover] && ![normal isEqual:pressed]);
    assert(disabled.alphaComponent < normal.alphaComponent);
    assert([name isEqual:NSAppearanceNameAqua]
        ? normal.redComponent < .1 : normal.redComponent > .9);
   }];
  }
  puts("PASS: SF Symbol availability/size, original-artwork fallback, floating scope, light/dark native state colors");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='lune-toolbar-') as directory:
    path = Path(directory) / 'test.mm'
    path.write_text(prefix + enum + selector + symbol + tests)
    binary = path.with_suffix('')
    subprocess.run(['xcrun', 'clang++', *(['-arch', args.arch] if args.arch else []),
                    '-std=c++20', '-fobjc-arc', '-framework', 'AppKit', str(path),
                    '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
