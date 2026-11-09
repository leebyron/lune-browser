#!/usr/bin/env python3
"""Exercise production header wheel routing and cross-window event coordinates.

The isolated AppKit fixture checks original-event delivery and routing lifetime.
Content selection and Chromium's renderer pipeline also need browser checks.
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
start = frame.index('@interface HeliumHeaderScrollRouter')
router = frame[start:frame.index('@interface HeliumChromeHitRegion', start)]
builder = (args.source / 'components/input/web_input_event_builders_mac.mm').read_text()
start = builder.index('struct EventLocationInfo')
location = builder[start:builder.index('bool IsSystemKeyEvent', start)]
cocoa = (args.source / 'content/app_shim_remote_cocoa/render_widget_host_view_cocoa.mm').read_text()
start = cocoa.index('- (void)shortCircuitScrollWheelEvent:')
end_cleanup = cocoa[start:cocoa.index('- (void)touchesMovedWithEvent:', start)]
start = cocoa.index('- (void)scrollWheel:')
wheel = cocoa[start:cocoa.index('// Called repeatedly during a pinch', start)]
prefix = r'''
#import <AppKit/AppKit.h>
#include <cassert>
#include <cmath>
namespace gfx {
struct PointF {
 float x = 0, y = 0;
 void SetPoint(float a, float b) { x = a; y = b; }
};
}
'''
end_prefix = r'''
struct WebMouseWheelEvent { int rails_mode = 0; };
struct WebMouseWheelEventBuilder {
 static WebMouseWheelEvent Build(NSEvent*, NSView*) { return {}; }
};
struct Filter { int UpdateRailsMode(WebMouseWheelEvent) { return 0; } };
struct Host {
 int forwarded = 0, routed = 0;
 void ForwardWheelEvent(WebMouseWheelEvent) { ++forwarded; }
 void RouteOrProcessWheelEvent(WebMouseWheelEvent) { ++routed; }
};
@protocol FixtureDelegate <NSObject>
- (BOOL)handleEvent:(NSEvent*)event;
@end
@interface ContentReceiver : NSView {
 @public
 id<FixtureDelegate> _responderDelegate;
 id _endWheelMonitor;
 Filter _mouseWheelFilter;
 Host host;
 Host* _hostHelper;
}
- (void)shortCircuitScrollWheelEvent:(NSEvent*)event;
@end
@implementation ContentReceiver
- (instancetype)init {
 self = [super init];
 if (self) _hostHelper = &host;
 return self;
}
'''
fixture = r'''
@interface ScrollReceiver : NSView
@property(nonatomic) int count;
@property(nonatomic, strong) NSEvent* lastEvent;
@end
@implementation ScrollReceiver
- (void)scrollWheel:(NSEvent*)event { ++_count; _lastEvent = event; }
@end
NSWindow* Window(NSRect rect) {
 NSWindow* w = [[NSWindow alloc] initWithContentRect:rect
   styleMask:NSWindowStyleMaskBorderless backing:NSBackingStoreBuffered defer:NO];
 w.releasedWhenClosed = NO;
 return w;
}
NSEvent* Scroll(NSWindow* window, NSPoint point, NSEventPhase phase,
                int momentum = 0, bool precise = true) {
 CGEventRef cg = CGEventCreateScrollWheelEvent(nullptr,
     precise ? kCGScrollEventUnitPixel : kCGScrollEventUnitLine, 2, -7, 3);
 // Test-only window attachment follows Chromium's cocoa_test_event_utils.
 // NSEvent has no public scroll-event constructor with a window argument.
 CGEventSetLocation(cg, CGPointMake(point.x,
     NSHeight(NSScreen.screens.firstObject.frame) - point.y));
 CGEventSetFlags(cg, kCGEventFlagMaskShift);
 int cg_phase = 0;
 if (phase & NSEventPhaseBegan) cg_phase |= kCGScrollPhaseBegan;
 if (phase & NSEventPhaseChanged) cg_phase |= kCGScrollPhaseChanged;
 if (phase & NSEventPhaseEnded) cg_phase |= kCGScrollPhaseEnded;
 if (phase & NSEventPhaseCancelled) cg_phase |= kCGScrollPhaseCancelled;
 CGEventSetIntegerValueField(cg, kCGScrollWheelEventScrollPhase, cg_phase);
 CGEventSetIntegerValueField(cg, kCGScrollWheelEventMomentumPhase, momentum);
 NSEvent* event = [NSEvent eventWithCGEvent:cg];
 [event setValue:window forKey:@"_window"];
 CFRelease(cg);
 assert(event.phase == phase);
 return event;
}
int main() {
 @autoreleasepool {
  [NSApplication sharedApplication];
  NSWindow* parent = Window(NSMakeRect(100, 200, 800, 600));
  NSWindow* child = Window(NSMakeRect(500, 700, 100, 36));
  NSWindow* other = Window(NSMakeRect(1000, 200, 800, 600));
  ScrollReceiver* left = [[ScrollReceiver alloc] initWithFrame:NSMakeRect(50, 40, 700, 550)];
  ScrollReceiver* right = [[ScrollReceiver alloc] initWithFrame:NSMakeRect(400, 0, 400, 600)];
  [parent.contentView addSubview:left];
  [parent.contentView addSubview:right];
  NSEvent* event = Scroll(child, NSMakePoint(11, 22), NSEventPhaseChanged);
  EventLocationInfo result = GetWebEventLocationForEventInView(event, left);
  assert(result.position_in_widget.x == 361 && result.position_in_widget.y == 68);
  EventLocationInfo original = GetWebEventLocationForEventInView(event, child.contentView);
  assert(result.position_in_screen.x == original.position_in_screen.x);
  assert(result.position_in_screen.y == original.position_in_screen.y);
  NSEvent* same = Scroll(parent, NSMakePoint(11, 22), NSEventPhaseNone, 0, false);
  result = GetWebEventLocationForEventInView(same, parent.contentView);
  assert(result.position_in_widget.x == 11 && result.position_in_widget.y == 578);
  puts("PASS: source/target window conversion, screen location, same-window coordinates");

  __block BOOL allowed = YES;
  __block ScrollReceiver* pointed = left;
  HeliumHeaderScrollRouter* router = [[HeliumHeaderScrollRouter alloc] init];
  router.resolveTarget = ^NSView*(NSEvent* e, NSView* momentum) {
   if (!allowed || (e.window != parent && e.window != child)) return nil;
   if (momentum && momentum.window != parent) return nil;
   return momentum ?: pointed;
  };
  NSEvent* begin = Scroll(child, NSMakePoint(11, 22), NSEventPhaseBegan);
  assert([router routeEvent:begin] == nil);
  assert(left.count == 1 && left.lastEvent == begin);
  assert(left.lastEvent.window == child && left.lastEvent.hasPreciseScrollingDeltas);
  assert(left.lastEvent.modifierFlags & NSEventModifierFlagShift);
  NSEvent* end = Scroll(child, NSMakePoint(11, 22), NSEventPhaseEnded);
  assert([router routeEvent:end] == nil);
  pointed = right;
  NSEvent* momentum = Scroll(child, NSMakePoint(90, 22), NSEventPhaseNone, 1);
  assert([router routeEvent:momentum] == nil);
  assert(left.count == 3 && right.count == 0 && left.lastEvent == momentum);
  NSEvent* momentum_end = Scroll(child, NSMakePoint(90, 22), NSEventPhaseNone, 3);
  assert([router routeEvent:momentum_end] == nil);
  assert(left.count == 4);
  assert([router routeEvent:momentum] == momentum);
  assert(right.count == 0);
  assert([router routeEvent:same] == nil && right.lastEvent == same);
  assert(!same.hasPreciseScrollingDeltas);
  puts("PASS: original precise/discrete events, single delivery, momentum target and end");

  assert([router routeEvent:begin] == nil);
  NSEvent* cancel = Scroll(child, NSMakePoint(11, 22), NSEventPhaseCancelled);
  assert([router routeEvent:cancel] == nil);
  assert([router routeEvent:momentum] == momentum);
  allowed = NO;
  assert([router routeEvent:begin] == begin);
  allowed = YES;
  NSEvent* foreign = Scroll(other, NSMakePoint(10, 10), NSEventPhaseBegan);
  assert([router routeEvent:foreign] == foreign);
  pointed = nil;
  assert([router routeEvent:begin] == begin);
  // A scroll delivered normally to page content must keep its native momentum.
  pointed = left;
  assert([router routeEvent:momentum] == momentum);
  NSEvent* click = [NSEvent mouseEventWithType:NSEventTypeLeftMouseDown
      location:NSMakePoint(10,10) modifierFlags:0 timestamp:1
      windowNumber:parent.windowNumber context:nil eventNumber:1 clickCount:1 pressure:1];
  assert([router routeEvent:click] == click);
  puts("PASS: cancellation, exclusions, other windows, missing targets, clicks unchanged");

  pointed = right;
  assert([router routeEvent:begin] == nil);
  [right removeFromSuperview];
  assert([router routeEvent:momentum] == momentum);
  __weak HeliumHeaderScrollRouter* weakRouter = router;
  [router shutdown];
  assert([router routeEvent:begin] == begin);
  router = nil;
  assert(!weakRouter);
  puts("PASS: detached target and monitor teardown");
  ContentReceiver* content = [[ContentReceiver alloc] init];
  [content scrollWheel:begin];
  assert(content->_endWheelMonitor);
  [content scrollWheel:end];
  assert(!content->_endWheelMonitor);
  assert(content->host.forwarded == 1 && content->host.routed == 2);
  [content scrollWheel:begin];
  // Model AppKit running the end monitor before ordinary view dispatch.
  [content shortCircuitScrollWheelEvent:end];
  [content scrollWheel:end];
  assert(!content->_endWheelMonitor && content->host.forwarded == 2);
  [content scrollWheel:begin];
  [content scrollWheel:cancel];
  assert(!content->_endWheelMonitor && content->host.forwarded == 3);
  puts("PASS: production wheel-end cleanup for forwarded, monitored and cancelled events");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='lune-header-scroll-') as temp:
    source = Path(temp) / 'test.mm'
    source.write_text(prefix + location + router + end_prefix + end_cleanup + wheel + "\n@end\n" + fixture)
    binary = source.with_suffix('')
    subprocess.run(['xcrun', 'clang++', '-arch', args.arch, '-std=c++20',
                    '-fobjc-arc', '-framework', 'AppKit', str(source),
                    '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
