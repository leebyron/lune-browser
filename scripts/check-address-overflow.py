#!/usr/bin/env python3
"""Check native address text alignment and clipping while URLs scroll."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
parser.add_argument('--report', type=Path, required=True)
parser.add_argument('--baseline', action='store_true')
args = parser.parse_args()
frame = (args.source / 'chrome/browser/ui/views/frame/browser_frame_view_mac.mm').read_text()
start = frame.index('static NSRect HeliumAddressEditingFrame(')
end = frame.index('// Keep the system focus indicator', start)
production = frame[start:end]
fixture = r'''
#import <AppKit/AppKit.h>
#include <algorithm>
#include <cassert>
#include <cstdio>

// The production parent installs word-boundary storage. Force its TextKit 1
// compatibility path here; word movement/storage has its own production test.
@interface HeliumWordTextFieldCell : NSTextFieldCell
@end
@implementation HeliumWordTextFieldCell
- (instancetype)initTextCell:(NSString*)value {
  if ((self = [super initTextCell:value])) {
    self.editable = YES;
    self.selectable = YES;
    self.scrollable = YES;
  }
  return self;
}
- (NSText*)setUpFieldEditorAttributes:(NSText*)text {
  NSText* result = [super setUpFieldEditorAttributes:text];
  (void)((NSTextView*)result).layoutManager;
  return result;
}
@end
PRODUCTION

static NSRect Viewport(NSTextField* field, NSView* host) {
  NSTextView* editor = (NSTextView*)field.currentEditor;
  NSView* viewport = [editor.superview isKindOfClass:NSClipView.class]
                         ? editor.superview : editor;
  return [host convertRect:viewport.bounds fromView:viewport];
}
static CGFloat TextStart(NSTextField* field, NSView* host) {
  NSTextView* editor = (NSTextView*)field.currentEditor;
  [editor.layoutManager ensureLayoutForTextContainer:editor.textContainer];
  NSRect character = [editor firstRectForCharacterRange:NSMakeRange(0, 1) actualRange:nil];
  NSRect inWindow = [editor.window convertRectFromScreen:character];
  return [host convertPoint:inWindow.origin fromView:nil].x;
}
static void Near(CGFloat actual, CGFloat expected) {
  if (std::abs(actual - expected) > .01) {
    fprintf(stderr, "geometry: actual %g, expected %g\n", actual, expected);
    abort();
  }
}
static void CheckViewport(NSTextField* field, NSView* host, NSRect available) {
  NSRect rect = Viewport(field, host);
  Near(NSMinX(rect), NSMinX(available) + 2);
  Near(NSMaxX(rect), NSMaxX(available) - 2);
}
int main() {
 @autoreleasepool {
  [NSApplication sharedApplication];
  NSWindow* window = [[NSWindow alloc]
      initWithContentRect:NSMakeRect(100, 100, 600, 80)
                styleMask:NSWindowStyleMaskTitled
                  backing:NSBackingStoreBuffered defer:NO];
  window.releasedWhenClosed = NO;
  NSTextField* field = [[NSTextField alloc] init];
  field.bezeled = NO;
  field.drawsBackground = NO;
  field.font = [NSFont systemFontOfSize:13];
  field.alignment = NSTextAlignmentLeft;
  field.lineBreakMode = NSLineBreakByTruncatingTail;
  field.usesSingleLineMode = YES;
  [window.contentView addSubview:field];
  [window makeKeyAndOrderFront:nil];
  NSRect available = NSMakeRect(40, 20, 400, 20);
  field.cell = [[HeliumWordTextFieldCell alloc] initTextCell:@""];
  field.bezeled = NO;
  field.drawsBackground = NO;
  field.font = [NSFont systemFontOfSize:13];
  field.frame = available;
  field.stringValue = @"https://example.com/";
  [window makeFirstResponder:field];
  CGFloat originalStart = TextStart(field, window.contentView);
  Near(originalStart, NSMinX(available) + 2);
  [window makeFirstResponder:nil];
  field.cell = [[CELL alloc] initTextCell:@""];
  field.bezeled = NO;
  field.drawsBackground = NO;
  field.font = [NSFont systemFontOfSize:13];
  field.lineBreakMode = NSLineBreakByTruncatingTail;
  field.usesSingleLineMode = YES;
  NSString* longURL = [@"https://example.com/" stringByPaddingToLength:500
      withString:@"long-path/" startingAtIndex:0];
  for (NSNumber* width in @[@400, @432, @180]) {
    available.size.width = width.doubleValue;
    for (NSString* value in @[@"", @"https://example.com/", longURL]) {
      [window makeFirstResponder:nil];
      field.frame = FRAME(available);
      field.stringValue = value;
      [window makeFirstResponder:field];
      NSTextView* editor = (NSTextView*)field.currentEditor;
      assert(editor && editor == window.firstResponder);
      [editor setSelectedRange:NSMakeRange(0, value.length)];
      CheckViewport(field, window.contentView, available);
      for (NSNumber* position in @[@0, @(value.length / 2), @(value.length)]) {
        [editor setSelectedRange:NSMakeRange(position.unsignedIntegerValue, 0)];
        [editor scrollRangeToVisible:editor.selectedRange];
        CheckViewport(field, window.contentView, available);
      }
      [editor setSelectedRange:NSMakeRange(0, 0)];
      [editor scrollRangeToVisible:editor.selectedRange];
      if (value.length) Near(TextStart(field, window.contentView), originalStart);
      for (NSNumber* resized in @[@160, @480, width]) {
        NSRect resizedArea = available;
        resizedArea.size.width = resized.doubleValue;
        field.frame = FRAME(resizedArea);
        [window displayIfNeeded];
        CheckViewport(field, window.contentView, resizedArea);
      }
    }
  }
  // Field editors are shared: returning to an ordinary native cell must
  // restore its native padding instead of inheriting the address policy.
  [window makeFirstResponder:nil];
  field.cell = [[HeliumWordTextFieldCell alloc] initTextCell:@""];
  field.bezeled = NO;
  field.drawsBackground = NO;
  field.font = [NSFont systemFontOfSize:13];
  field.frame = NSMakeRect(40, 20, 400, 20);
  field.stringValue = @"https://example.com/";
  [window makeFirstResponder:field];
  Near(TextStart(field, window.contentView), originalStart);
  [window makeFirstResponder:nil];
  [window close];
  puts("PASS: short-text origin; fixed clipping at start/middle/end; empty input; reload/scoped widths; resize; shared-editor reset");
 }
}
'''
fixture = fixture.replace('PRODUCTION', production)
fixture = fixture.replace('CELL', 'HeliumWordTextFieldCell' if args.baseline else 'HeliumAddressTextFieldCell')
fixture = fixture.replace('FRAME(available)', 'available' if args.baseline else 'HeliumAddressEditingFrame(available)')
fixture = fixture.replace('FRAME(resizedArea)', 'resizedArea' if args.baseline else 'HeliumAddressEditingFrame(resizedArea)')
with tempfile.TemporaryDirectory(prefix='lune-address-overflow-') as temporary:
    path = Path(temporary)
    (path / 'check.mm').write_text(fixture)
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-fobjc-arc', '-arch', args.arch,
                    '-framework', 'AppKit', str(path / 'check.mm'), '-o', str(path / 'check')], check=True)
    result = subprocess.run(['/usr/bin/arch', '-' + args.arch, str(path / 'check')],
                            capture_output=True, text=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({'architecture': args.arch, 'baseline': args.baseline,
                                      'passed': result.returncode == 0, 'exit_code': result.returncode,
                                      'output': result.stdout + result.stderr}, indent=2) + '\n')
    print(result.stdout + result.stderr, end='')
    result.check_returncode()
