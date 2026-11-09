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
start = text.index('@interface HeliumCommandMaterial')
end = text.index('@interface HeliumCommandResults', start)
# Compile the production material view without Chromium's unrelated dependencies.
fixture='''
int main(){@autoreleasepool{
 [NSApplication sharedApplication];
 HeliumCommandMaterial* view=[[HeliumCommandMaterial alloc] initWithFrame:NSMakeRect(0,0,600,52)];
 assert(!view.clipsToBounds);
 assert(fabs(view.shadow.shadowColor.alphaComponent-.05)<.001);
 assert(view.shadow.shadowBlurRadius==10);
 assert(view.shadow.shadowOffset.height==-3);
 for(NSValue* size in @[[NSValue valueWithSize:NSMakeSize(600,52)], [NSValue valueWithSize:NSMakeSize(600,320)], [NSValue valueWithSize:NSMakeSize(300,164)]]){
  [view setFrameSize:size.sizeValue];
  assert(CGRectEqualToRect(CGPathGetBoundingBox(view.layer.shadowPath),view.bounds));
  assert(!CGPathContainsPoint(view.layer.shadowPath,nullptr,CGPointMake(0,0),false));
  assert(CGPathContainsPoint(view.layer.shadowPath,nullptr,CGPointMake(20,20),false));
 }
 puts("PASS: subtle native material shadow, unclipped rounded path follows empty/full/narrow dimensions");
}}
'''
with tempfile.TemporaryDirectory(prefix='lune-command-shadow-') as tmp:
    path = Path(tmp)
    check = path / 'check.mm'
    check.write_text('#import <AppKit/AppKit.h>\n#import <QuartzCore/QuartzCore.h>\n#include <cassert>\n#include <cmath>\n' + text[start:end] + fixture)
    binary = path / 'check'
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                    '-arch', args.arch, '-framework', 'AppKit',
                    '-framework', 'QuartzCore', str(check), '-o', str(binary)], check=True)
    subprocess.run(['/usr/bin/arch', '-' + args.arch, str(binary)], check=True)
