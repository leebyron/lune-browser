#!/usr/bin/env python3
"""Check native address and glass cursor ownership across focus changes."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
args = parser.parse_args()
src = args.source.resolve()
frame = (src/'chrome/browser/ui/views/frame/browser_frame_view_mac.mm').read_text()
start = frame.index('@interface HeliumGlassAddressField :')
end = frame.index('// Preserve AppKit', start)
field = frame[start:end]
surface_start = frame.index('- (void)resetCursorRects', frame.index('@implementation HeliumFloatingAddressBar'))
surface_end = frame.index('- (instancetype)initWithBrowserView:', surface_start)
surface_methods = frame[surface_start:surface_end]
fixture = r'''
#import <AppKit/AppKit.h>
#import "chrome/browser/ui/views/helium/native_text_field_mac.h"
#include <cassert>
ADDRESS_FIELD
@interface CursorApp : NSApplication
@end
@implementation CursorApp
- (BOOL)isActive { return YES; }
@end
@interface ArrowSurface : NSView
@end
@implementation ArrowSurface
- (void)resetCursorRects { [self addCursorRect:self.bounds cursor:NSCursor.arrowCursor]; }
- (void)mouseMoved:(NSEvent*)event { [NSCursor.arrowCursor set]; }
@end
@interface CursorSurface : ArrowSurface {
@public HeliumGlassAddressField* _address;
}
@property NSMutableArray* regions;
@end
@implementation CursorSurface
- (void)addCursorRect:(NSRect)rect cursor:(NSCursor*)cursor {
  [self.regions addObject:@{ @"rect": [NSValue valueWithRect:rect], @"cursor": cursor }];
  [super addCursorRect:rect cursor:cursor];
}
SURFACE_METHODS
@end
static void CheckSurface(CursorSurface* surface, NSPoint point, NSCursor* expected) {
  [surface discardCursorRects]; [surface.regions removeAllObjects];
  [surface resetCursorRects];
  NSInteger matches=0;
  for (NSDictionary* region in surface.regions) {
    if (NSPointInRect(point, [region[@"rect"] rectValue])) {
      assert(region[@"cursor"] == expected); ++matches;
    }
  }
  assert(matches==1);
}
static void CheckForwardedMove(CursorSurface* surface, NSPoint local, NSCursor* expected) {
  NSPoint point=[surface convertPoint:local toView:nil];
  NSEvent* event=[NSEvent mouseEventWithType:NSEventTypeMouseMoved location:point
      modifierFlags:0 timestamp:0 windowNumber:surface.window.windowNumber
      context:nil eventNumber:1 clickCount:0 pressure:0];
  // NSTextView first installs its I-beam, then forwards to the glass ancestor.
  [NSCursor.IBeamCursor set]; [surface mouseMoved:event];
  assert(NSCursor.currentCursor == expected);
}
@interface CursorWindow : NSWindow
@property NSInteger invalidations;
@end
@implementation CursorWindow
- (BOOL)isKeyWindow { return YES; }
- (void)invalidateCursorRectsForView:(NSView*)view {
  ++self.invalidations;
  [super invalidateCursorRectsForView:view];
}
@end
@interface CursorField : HeliumGlassAddressField
@property NSCursor* registeredCursor;
@property NSRect registeredBounds;
@property NSInteger discards;
@end
@implementation CursorField
- (void)discardCursorRects {
  ++self.discards;
  [super discardCursorRects];
}
- (void)addCursorRect:(NSRect)rect cursor:(NSCursor*)cursor {
  self.registeredCursor = cursor;
  self.registeredBounds = rect;
  [super addCursorRect:rect cursor:cursor];
}
@end
static void CheckCursor(CursorField* field, NSCursor* expected) {
  [field discardCursorRects];
  [field resetCursorRects];
  assert(field.registeredCursor == expected);
  if (expected == NSCursor.arrowCursor) {
    assert(NSEqualRects(field.registeredBounds, field.bounds));
  } else {
    // AppKit limits its text cursor to the native text area inside the field.
    assert(!NSIsEmptyRect(NSIntersectionRect(field.registeredBounds, field.bounds)));
  }
}
int main() { @autoreleasepool {
  [CursorApp sharedApplication];
  CursorWindow* window = [[CursorWindow alloc]
      initWithContentRect:NSMakeRect(0,0,600,200)
      styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
  CursorField* field = [[CursorField alloc] initWithFrame:NSMakeRect(20,80,420,30)];
  field.stringValue = @"https://example.com/";
  CursorSurface* surface=[[CursorSurface alloc] initWithFrame:window.contentView.bounds];
  surface.regions=[NSMutableArray array]; surface->_address=field;
  [window.contentView addSubview:surface];
  [surface addSubview:field];
  NSPoint text=NSMakePoint(200,95), chrome=NSMakePoint(5,5);
  CheckSurface(surface,text,NSCursor.arrowCursor);
  CheckForwardedMove(surface,text,NSCursor.arrowCursor);
  assert(!field.acceptsFirstResponder);
  CheckCursor(field, NSCursor.arrowCursor);
  NSInteger invalidations = window.invalidations;
  for (int cycle=0; cycle<3; ++cycle) {
    NSInteger discards = field.discards;
    field.userEditing = YES;
    assert(field.discards > discards);
    assert(window.invalidations > invalidations);
    invalidations = window.invalidations;
    assert([window makeFirstResponder:field]);
    assert(field.currentEditor);
    assert(window.firstResponder == field.currentEditor);
    CheckCursor(field, NSCursor.IBeamCursor);
    CheckSurface(surface,text,NSCursor.IBeamCursor);
    CheckSurface(surface,chrome,NSCursor.arrowCursor);
    CheckForwardedMove(surface,text,NSCursor.IBeamCursor);
    CheckForwardedMove(surface,chrome,NSCursor.arrowCursor);
    // Scope/layout changes must preserve the cursor over the complete field.
    field.frame = NSMakeRect(100,80,340,30);
    CheckCursor(field, NSCursor.IBeamCursor);
    CheckSurface(surface,text,NSCursor.IBeamCursor);
    CheckSurface(surface,NSMakePoint(30,95),NSCursor.arrowCursor);
    CheckForwardedMove(surface,NSMakePoint(30,95),NSCursor.arrowCursor);
    [window makeFirstResponder:nil];
    CheckForwardedMove(surface,text,NSCursor.arrowCursor);
    discards = field.discards;
    field.userEditing = NO;
    assert(field.discards > discards);
    assert(window.invalidations > invalidations);
    invalidations = window.invalidations;
    assert(!field.acceptsFirstResponder);
    CheckSurface(surface,text,NSCursor.arrowCursor);
    CheckForwardedMove(surface,text,NSCursor.arrowCursor);
    CheckCursor(field, NSCursor.arrowCursor);
    field.frame = NSMakeRect(20,80,420,30);
    CheckCursor(field, NSCursor.arrowCursor);
  }
  puts("PASS: idle arrow, focused I-beam, glass structural regions, forwarded native mouse movement, blur, repeated focus and resized bounds");
} }
'''.replace('ADDRESS_FIELD', field).replace('SURFACE_METHODS', surface_methods)
with tempfile.TemporaryDirectory(prefix='lune-address-cursor-') as tmp:
    out = Path(tmp)
    (out/'check.mm').write_text(fixture)
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc', '-I', str(src),
                    '-arch', args.arch, '-framework', 'AppKit',
                    str(out/'check.mm'),
                    str(src/'chrome/browser/ui/views/helium/native_text_field_mac.mm'),
                    '-o', str(out/'check')], check=True)
    subprocess.run(['/usr/bin/arch', '-'+args.arch, str(out/'check')], check=True)
