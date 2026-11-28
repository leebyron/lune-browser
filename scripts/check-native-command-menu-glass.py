#!/usr/bin/env python3
"""Check native command-menu tone and editor lifetime across result sizes.

Compiles the production material and construction, then exercises light/dark
appearance, three backdrops, and repeated compact/expanded/narrow resizing.
Effective appearance checks do not replace compositor-level visual review.
"""
from pathlib import Path
import argparse
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
args = parser.parse_args()
src = args.source
arch = args.arch
name='chrome/browser/ui/helium/helium_command_bar_view_mac.mm'
text=(src/name).read_text()
constants=text[text.index('constexpr int kShadowTopInset'):text.index('constexpr gfx::Insets')] + text[text.index('constexpr int kWidth'):text.index('// The native host handles clicks')]
material=text[text.rindex('namespace {',0,text.index('constexpr CGFloat kCommandShadowBlur')):text.index('@interface HeliumCommandResults')]
start=text.index('  if (@available(macOS 26, *)) {',text.index('HeliumCommandBarView::HeliumCommandBarView'))
end=text.index('  if (!native_->material)',start)
construction=text[start:end].replace('native_->material = material;','return material;')
fixture=r'''
static NSView* Create(BOOL dark, NSView* pane) {
 NSAppearance* appearance=[NSAppearance appearanceNamed:dark?NSAppearanceNameDarkAqua:NSAppearanceNameAqua];
 void* browser_view=nullptr;
 CONSTRUCTION
 return nil;
}
int main() { @autoreleasepool {
 [NSApplication sharedApplication];
 if (@available(macOS 26,*)) {
  NSWindow* window=[[NSWindow alloc] initWithContentRect:NSMakeRect(80,80,800,600) styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
  window.contentView.wantsLayer=YES;
  [window orderFront:nil];
  for (BOOL dark : {NO,YES}) {
   NSView* pane=[[NSView alloc] initWithFrame:NSMakeRect(0,0,600,52)];
   pane.autoresizingMask=NSViewWidthSizable|NSViewHeightSizable;
   NSTextField* input=[[NSTextField alloc] initWithFrame:NSMakeRect(16,14,200,24)];input.bordered=NO;input.drawsBackground=NO;input.stringValue=@"test query"; [pane addSubview:input];
   NSView* material=Create(dark,pane);[window.contentView addSubview:material];
   auto* frost=(NSVisualEffectView*)material.subviews[0];
   auto* backing=material.subviews[1];
   auto* glass=(NSGlassEffectView*)material.subviews[2];
   assert(material.subviews.count==4 && material.subviews[3]==pane);
   [window makeKeyWindow];[window makeFirstResponder:input];
   NSTextView* editor=(NSTextView*)input.currentEditor;assert(editor);
   editor.selectedRange=NSMakeRange(2,3);
   for (NSColor* background in @[NSColor.blackColor,NSColor.whiteColor,[NSColor colorWithSRGBRed:1 green:0 blue:0 alpha:1]]) {
    window.contentView.layer.backgroundColor=background.CGColor;
    for (CGFloat width : {600.,360.,220.}) for (CGFloat height : {52.,111.,163.,215.,267.,319.,52.,319.,52.}) {
     [material setFrameSize:NSMakeSize(width,height)];
     [window.contentView layoutSubtreeIfNeeded];
     [CATransaction flush];
     NSDate* until=[NSDate dateWithTimeIntervalSinceNow:.02];
     while ([until timeIntervalSinceNow]>0) [[NSRunLoop currentRunLoop] runMode:NSDefaultRunLoopMode beforeDate:until];
     assert(CGRectEqualToRect(frost.frame,material.bounds));
     assert(frost.material==NSVisualEffectMaterialPopover);
     assert(frost.blendingMode==NSVisualEffectBlendingModeBehindWindow);
     assert(frost.alphaValue==1);
     assert(CGRectEqualToRect(backing.frame,material.bounds));
     assert(CGRectEqualToRect(glass.frame,material.bounds));
     assert(CGRectEqualToRect(pane.frame,material.bounds));
     assert(pane.superview==material && pane.alphaValue==1);
     assert(fabs(glass.alphaValue-.3)<.001);
     assert(glass.style==NSGlassEffectViewStyleClear);
     assert([glass.tintColor isEqual:helium::NativeGlassThemeTintColor(nullptr)]);
     assert(material.layer.sublayers.firstObject.contents);
     assert(input.currentEditor==editor);assert(NSEqualRanges(editor.selectedRange,NSMakeRange(2,3)));
     NSString* actual=[pane.effectiveAppearance bestMatchFromAppearancesWithNames:@[NSAppearanceNameAqua,NSAppearanceNameDarkAqua]];
     NSString* expected=dark?NSAppearanceNameDarkAqua:NSAppearanceNameAqua;
     if(![actual isEqual:expected]) {fprintf(stderr,"tone flipped at %gx%g: %s expected %s\n",width,height,actual.UTF8String,expected.UTF8String);abort();}
     assert(!backing.hidden);
     assert(fabs(CGColorGetAlpha(backing.layer.backgroundColor) - .32) < .001);
     NSColor* neutral = [[NSColor colorWithCGColor:backing.layer.backgroundColor]
         colorUsingColorSpace:NSColorSpace.sRGBColorSpace];
     const CGFloat expectedChannel = dark ? 0 : 1;
     assert(fabs(neutral.redComponent - expectedChannel) < .001);
     assert(fabs(neutral.greenComponent - expectedChannel) < .001);
     assert(fabs(neutral.blueComponent - expectedChannel) < .001);
    }
   }
   [material removeFromSuperview];
  }
  [window orderOut:nil];
  puts("PASS: production Clear glass retains profile tone, attached content, editor focus/selection, backing and rounded shadow across 162 size/background/appearance states");
 }
} }
'''.replace('CONSTRUCTION',construction)
code='#import <AppKit/AppKit.h>\n#import <QuartzCore/QuartzCore.h>\n#include <algorithm>\n#include <array>\n#include <cmath>\n#include <cstdint>\n#include <cassert>\n#include <initializer_list>\n#include "chrome/browser/ui/helium/native_result_row_mac.h"\nnamespace helium { NSColor* NativeGlassThemeTintColor(void*) { return [NSColor colorWithSRGBRed:.7 green:.2 blue:.4 alpha:.05]; } }\n'+constants+material+fixture
with tempfile.TemporaryDirectory(prefix='lune-command-menu-glass-') as tmp:
    out = Path(tmp)
    (out/'check.mm').write_text(code)
    subprocess.run(['xcrun','clang++','-std=c++20','-fobjc-arc','-I',str(src),'-arch',arch,'-framework','AppKit','-framework','QuartzCore',str(out/'check.mm'),'-o',str(out/'check')],check=True)
    subprocess.run(['/usr/bin/arch','-'+arch,str(out/'check')],check=True)
