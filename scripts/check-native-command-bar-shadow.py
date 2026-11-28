#!/usr/bin/env python3
"""Check the production Command-T shadow silhouette with native AppKit."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
args = parser.parse_args()
source = args.source / 'chrome/browser/ui/helium/helium_command_bar_view_mac.mm'
text = source.read_text()
constants = text[text.index('constexpr int kShadowTopInset'):text.index('constexpr gfx::Insets')] + text[text.index('constexpr int kWidth'):text.index('// The native host handles clicks')]
start = text.rindex('namespace {',0,text.index('constexpr CGFloat kCommandShadowBlur'))
end = text.index('@interface HeliumCommandResults', start)
# Compile the production material view without Chromium's unrelated dependencies.
fixture=r'''
static uint8_t Alpha(CGImageRef image, CFDataRef bytes, size_t x, size_t y) {
  return CFDataGetBytePtr(bytes)[y * CGImageGetBytesPerRow(image) + x * 4 + 3];
}
int main() {
 @autoreleasepool {
  [NSApplication sharedApplication];
  auto* material = [[HeliumCommandMaterial alloc] initWithFrame:NSMakeRect(0,0,720,111)];
  assert(!material.clipsToBounds && kCommandShadowBlur==64 && kCommandShadowOffset==32);
  for (int panelWidth : {220,360,720}) {
   const int width=panelWidth+2*kShadowSideInset;
   CGImageRef reference=CreateCommandShadowImage(
       CGSizeMake(panelWidth,111), CGSizeMake(width,111+kShadowTopInset+kShadowBottomInset));
   assert(reference);
   CFDataRef refBytes=CGDataProviderCopyData(CGImageGetDataProvider(reference));
   for (int panelHeight : {52,111,163,215,267,319,111}) {
    [material setFrameSize:NSMakeSize(panelWidth,panelHeight)];
    CALayer* shadow=material.layer.sublayers.firstObject;
    assert(shadow.mask==nil && !shadow.masksToBounds && shadow.contents);
    CGImageRef image=(__bridge CGImageRef)shadow.contents;
    assert(CGImageGetWidth(image)==width);
    size_t height=CGImageGetHeight(image);
    assert(height==panelHeight+kShadowTopInset+kShadowBottomInset);
    CFDataRef bytes=CGDataProviderCopyData(CGImageGetDataProvider(image));
    // Below a short panel the offset caster's midpoint can be a few
    // points beyond the visible bottom edge. Compare the lower fade
    // starting just past that midpoint.
    const int bottomStart=std::max<int>(0,kCommandShadowOffset-panelHeight/2);
    for (int x=0; x<width; ++x) {
      for (int margin=0; margin<4; ++margin) {
       assert(Alpha(image,bytes,x,margin)==0);
       assert(Alpha(image,bytes,x,height-1-margin)==0);
      }
      for (int d=0; d<kShadowTopInset; ++d)
       assert(Alpha(image,bytes,x,d)==Alpha(reference,refBytes,x,d));
      for (int d=bottomStart; d<kShadowBottomInset; ++d)
       assert(Alpha(image,bytes,x,kShadowTopInset+panelHeight+d)==
              Alpha(reference,refBytes,x,kShadowTopInset+111+d));
    }
    for (size_t y=0; y<height; ++y) {
      for (int margin=0; margin<4; ++margin) {
       assert(Alpha(image,bytes,margin,y)==0);
       assert(Alpha(image,bytes,width-1-margin,y)==0);
      }
    }
    for (int x=0; x<kShadowSideInset; ++x)
      assert(Alpha(image,bytes,x,kShadowTopInset+kCommandShadowOffset+panelHeight/2)==
             Alpha(reference,refBytes,x,kShadowTopInset+kCommandShadowOffset+111/2));
    assert(Alpha(image,bytes,width/2,kShadowTopInset+panelHeight+12)>
           Alpha(image,bytes,width/2,kShadowTopInset-12));
    CFRelease(bytes);
   }
   CFRelease(refBytes);
   CGImageRelease(reference);
  }
  puts("PASS: one continuous outline falloff retains upper, side and lower profiles and fades to transparent before the popup boundary");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='lune-command-shadow-') as tmp:
    path = Path(tmp)
    check = path / 'check.mm'
    check.write_text('#import <AppKit/AppKit.h>\n#import <QuartzCore/QuartzCore.h>\n#include <algorithm>\n#include <array>\n#include <cmath>\n#include <cstdint>\n#include <cassert>\n#include <initializer_list>\n' + '#include "chrome/browser/ui/helium/native_result_row_mac.h"\n' + constants + text[start:end] + fixture)
    binary = path / 'check'
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                    '-I', str(args.source), '-arch', args.arch, '-framework', 'AppKit',
                    '-framework', 'QuartzCore', str(check), '-o', str(binary)], check=True)
    subprocess.run(['/usr/bin/arch', '-' + args.arch, str(binary)], check=True)
