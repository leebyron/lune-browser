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
constants = text[text.index('constexpr int kWidth'):text.index('int CommandBarHeight')]
start = text.index('@interface HeliumCommandMaterial')
end = text.index('@interface HeliumCommandResults', start)
# Compile the production material view without Chromium's unrelated dependencies.
fixture='''
int main(){@autoreleasepool{
 [NSApplication sharedApplication];
 HeliumCommandMaterial* view=[[HeliumCommandMaterial alloc] initWithFrame:NSMakeRect(0,0,720,52)];
 assert(!view.clipsToBounds);
 assert(kGlassCornerRadius == 18);
 assert(kGlassCornerRadius == kHeliumNativeResultInset + kHeliumNativeResultCornerRadius);
 assert(kResultsBottomInset + kHeliumNativeResultVerticalInset == kHeliumNativeResultInset);
 assert(fabs(view.shadow.shadowColor.alphaComponent-.25)<.001);
 assert(view.shadow.shadowBlurRadius==64);
 assert(NSEqualSizes(view.shadow.shadowOffset, NSMakeSize(0, -32)));
 for(NSValue* size in @[[NSValue valueWithSize:NSMakeSize(720,52)], [NSValue valueWithSize:NSMakeSize(720,319)], [NSValue valueWithSize:NSMakeSize(300,163)]]){
  [view setFrameSize:size.sizeValue];
  assert(CGRectEqualToRect(CGPathGetBoundingBox(view.layer.shadowPath),view.bounds));
  assert(!CGPathContainsPoint(view.layer.shadowPath,nullptr,CGPointMake(0,0),false));
  assert(CGPathContainsPoint(view.layer.shadowPath,nullptr,CGPointMake(20,20),false));
 }
 puts("PASS: diffuse downward native material shadow, unclipped rounded path follows empty/full/narrow dimensions");
}}
'''
with tempfile.TemporaryDirectory(prefix='lune-command-shadow-') as tmp:
    path = Path(tmp)
    check = path / 'check.mm'
    check.write_text('#import <AppKit/AppKit.h>\n#import <QuartzCore/QuartzCore.h>\n#include <cassert>\n#include <cmath>\n' + '#include "chrome/browser/ui/helium/native_result_row_mac.h"\n' + constants + text[start:end] + fixture)
    binary = path / 'check'
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                    '-I', str(args.source), '-arch', args.arch, '-framework', 'AppKit',
                    '-framework', 'QuartzCore', str(check), '-o', str(binary)], check=True)
    subprocess.run(['/usr/bin/arch', '-' + args.arch, str(binary)], check=True)
