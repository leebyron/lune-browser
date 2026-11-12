#!/usr/bin/env python3
"""Exercise production native text focus restoration and dismissal decisions.

App activation and Chromium's intervening responder reset are simulated with
real AppKit field editors. Owner review covers actual app switching.
"""
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
start = frame.index('- (void)controlTextDidEndEditing:')
end = frame.index('\n- (void)reloadSuggestions', start)
address_end = frame[start:end].replace('HeliumFloatingAddressBar', 'AddressOwner')
command = (src/'chrome/browser/ui/helium/helium_command_bar_view_mac.mm').read_text()
start = command.index('  if (!active) {', command.index('void HeliumCommandBarView::OnWidgetActivationChanged'))
end = command.index('\nvoid HeliumCommandBarView::ContentsChanged', start)
command_end = command[start:end].rsplit('}', 1)[0]
monitor_start = command.index('      handler:^NSEvent*(NSEvent* event) {', command.index('dismissal_monitor = [NSEvent'))
monitor_end = command.index('      }];', monitor_start)
monitor_handler = command[monitor_start:monitor_end] + '      };'
monitor_handler = monitor_handler.replace('      handler:', '  EventHandler handler = ', 1)
# Exercise the real early inactivity gate, which precedes pointer retention.
start = frame.index('  if (!HasFloatingAddressBar() ||', frame.index(
    'void BrowserFrameViewMac::UpdateFloatingAddressBar()'))
guard = frame[start:frame.index(' {', start)]
guard = guard.replace('HasFloatingAddressBar()', 'has_address').replace(
    'browser_view->IsZenModeTopChromePinned()', 'pinned').replace(
    'GetWidget()->IsActive()', 'widget_active').replace('NSApp.active', 'app_active')
field_start = frame.index('@interface HeliumGlassAddressField :')
field_end = frame.index('// Preserve AppKit', field_start)
address_field = frame[field_start:field_end]
transfer_start = frame.index('  _address.onFocusTransferred = ^{')
transfer_end = frame.index('\n  };', transfer_start) + len('\n  };')
transfer = frame[transfer_start:transfer_end].replace(
    '_address.onFocusTransferred =', 'field.onFocusTransferred =', 1).replace(
    'HeliumFloatingAddressBar', 'AddressOwner')
fixture = r'''
#import <AppKit/AppKit.h>
#import "chrome/browser/ui/views/helium/native_text_field_mac.h"
#include <cassert>
#include <memory>

@interface TestApplication : NSApplication
@property BOOL testActive;
@end
@implementation TestApplication
- (BOOL)isActive { return self.testActive; }
@end
@interface TestWindow : NSWindow
@property BOOL testKey;
@property BOOL testMain;
@end
@implementation TestWindow
- (BOOL)isKeyWindow { return self.testKey; }
- (BOOL)isMainWindow { return self.testMain; }
- (void)makeKeyWindow {
  self.testKey = YES;
  [NSNotificationCenter.defaultCenter postNotificationName:
      NSWindowDidBecomeKeyNotification object:self];
}
@end
ADDRESS_FIELD
@interface RingField : HeliumGlassAddressField
@property NSInteger maskChanges;
@end
@implementation RingField
- (void)noteFocusRingMaskChanged { ++self.maskChanges; [super noteFocusRingMaskChanged]; }
@end
@interface AddressOwner : NSObject <NSTextFieldDelegate> {
@public HeliumNativeTextField* _address; BOOL _editing;
}
@property NSInteger finishes;
- (void)finishEditing;
- (BOOL)isEditing;
- (NSWindow*)window;
@end
@implementation AddressOwner
- (void)finishEditing {
  ++self.finishes;
  _editing=NO;
  [_address cancelFocusRestoration];
}
- (BOOL)isEditing { return _editing || _address.currentEditor != nil; }
- (NSWindow*)window { return _address.window; }
ADDRESS_END
@end
int action_order=0;
struct Widget : std::enable_shared_from_this<Widget> {
  bool active = true;
  int closes = 0;
  int close_order = 0;
  int activations = 0;
  std::weak_ptr<Widget> GetWeakPtr() { return weak_from_this(); }
  bool IsActive() { return active; }
  bool IsClosed() { return closes > 0; }
  void Close() { ++closes; }
  void CloseNow() { ++closes; close_order=++action_order; }
  void Activate() { active=true; ++activations; }
};
// Chromium's WeakPtr has pointer syntax and a bool conversion.
struct WeakWidget {
  std::weak_ptr<Widget> value;
  operator bool() const { return !value.expired(); }
  Widget* operator->() const { return value.lock().get(); }
};
struct WidgetAdapter {
  std::shared_ptr<Widget> value;
  WeakWidget GetWeakPtr() { return {value}; }
};
void ActivationChanged(WidgetAdapter* widget, bool active) {
COMMAND_END
}

@interface HeliumCommandPane : NSView
@property(nonatomic,strong) HeliumNativeTextField* input;
@property(nonatomic,copy) BOOL (^onCommand)(SEL);
@end
@implementation HeliumCommandPane
@end
struct Browser {
  Widget parent;
  int focus_calls=0;
  int focus_order=0;
  Widget* GetWidget() { return &parent; }
  void SetFocusToLocationBar(bool user_initiated) {
    assert(user_initiated); ++focus_calls; focus_order=++action_order;
  }
};
struct WeakBrowser {
  std::weak_ptr<Browser> value;
  operator bool() const { return !value.expired(); }
  Browser* operator->() const { return value.lock().get(); }
};
typedef NSEvent* (^EventHandler)(NSEvent*);
EventHandler MakeDismissalHandler(WeakWidget weak_widget, HeliumCommandPane* pane,
                                  WeakBrowser weak_browser={}) {
  __weak HeliumCommandPane* weak_pane = pane;
MONITOR_HANDLER
  return handler;
}
TestWindow* Window();
void Drain();
void CheckDismissalWithoutEditor() {
  TestWindow* parent=Window(); parent.testKey=YES;
  TestWindow* popup=Window(); popup.testKey=NO;
  [popup setFrame:NSMakeRect(100,100,600,200) display:NO];
  [parent addChildWindow:popup ordered:NSWindowAbove];
  auto* pane=[[HeliumCommandPane alloc] initWithFrame:NSMakeRect(40,40,500,100)];
  [popup.contentView addSubview:pane];
  pane.input=[[HeliumNativeTextField alloc] initWithFrame:NSMakeRect(10,20,300,24)];
  [pane addSubview:pane.input];
  __block int escapes=0;
  pane.onCommand=^BOOL(SEL command) { assert(command==@selector(cancelOperation:)); ++escapes; return YES; };
  auto widget=std::make_shared<Widget>(); widget->active=false;
  EventHandler handler=MakeDismissalHandler({widget},pane);
  assert(!pane.input.currentEditor);
  // Deliberately leave the popup inactive and the field editor unfocused after
  // return. Native dismissal cannot depend on either of those being repaired.
  NSEvent* escape=[NSEvent keyEventWithType:NSEventTypeKeyDown location:NSZeroPoint
      modifierFlags:0 timestamp:0 windowNumber:parent.windowNumber context:nil
      characters:@"\x1b" charactersIgnoringModifiers:@"\x1b" isARepeat:NO keyCode:53];
  assert(handler(escape)==nil); assert(escapes==1);
  NSEvent* key=[NSEvent keyEventWithType:NSEventTypeKeyDown location:NSZeroPoint
      modifierFlags:0 timestamp:0 windowNumber:parent.windowNumber context:nil
      characters:@"x" charactersIgnoringModifiers:@"x" isARepeat:NO keyCode:7];
  assert(handler(key)==key);
  NSEvent* modified=[NSEvent keyEventWithType:NSEventTypeKeyDown location:NSZeroPoint
      modifierFlags:NSEventModifierFlagCommand timestamp:0 windowNumber:parent.windowNumber context:nil
      characters:@"\x1b" charactersIgnoringModifiers:@"\x1b" isARepeat:NO keyCode:53];
  assert(handler(modified)==modified); assert(escapes==1);
  NSPoint inside=[pane convertPoint:NSMakePoint(20,20) toView:nil];
  NSEvent* click=[NSEvent mouseEventWithType:NSEventTypeLeftMouseDown location:inside
      modifierFlags:0 timestamp:0 windowNumber:popup.windowNumber context:nil eventNumber:1 clickCount:1 pressure:1];
  assert(handler(click)==click); assert(widget->closes==0);
  assert([popup makeFirstResponder:pane.input]);
  assert(pane.input.currentEditor);
  [NSNotificationCenter.defaultCenter postNotificationName:
      NSApplicationWillResignActiveNotification object:NSApp];
  assert(pane.input.preservingFocus);
  [popup makeFirstResponder:nil];
  NSEvent* background=[NSEvent mouseEventWithType:NSEventTypeLeftMouseDown location:NSMakePoint(0,0)
      modifierFlags:0 timestamp:0 windowNumber:parent.windowNumber context:nil eventNumber:2 clickCount:1 pressure:1];
  assert(handler(background)==background); assert(widget->closes==1);
  assert(!pane.input.preservingFocus);
  // Closing the widget disables the monitor before deferred native destruction.
  assert(handler(escape)==escape); assert(escapes==1);
  widget.reset(); assert(handler(escape)==escape);
  auto transfer_widget=std::make_shared<Widget>();
  auto browser=std::make_shared<Browser>();
  EventHandler transfer_handler=MakeDismissalHandler({transfer_widget},pane,{browser});
  NSEvent* cmdl=[NSEvent keyEventWithType:NSEventTypeKeyDown location:NSZeroPoint
      modifierFlags:NSEventModifierFlagCommand timestamp:0 windowNumber:popup.windowNumber context:nil
      characters:@"l" charactersIgnoringModifiers:@"l" isARepeat:NO keyCode:37];
  assert(transfer_handler(cmdl)==nil);
  assert(transfer_widget->closes==0 && browser->focus_calls==0);
  Drain();
  assert(transfer_widget->closes==1 && browser->focus_calls==1);
  assert(browser->parent.activations==1);
  assert(transfer_widget->close_order < browser->focus_order);
  // The deferred handoff safely tolerates browser destruction.
  auto dying_widget=std::make_shared<Widget>();
  auto dying_browser=std::make_shared<Browser>();
  EventHandler dying_handler=MakeDismissalHandler({dying_widget},pane,{dying_browser});
  assert(dying_handler(cmdl)==nil); dying_browser.reset(); Drain();
  assert(dying_widget->closes==1);

}

bool HeaderHidden(bool has_address, bool pinned, bool editing,
                  bool widget_active, bool app_active, bool command_bar_open,
                  bool bubble_open, bool dragging=false, bool resizing=false,
                  bool window_menu_open=false, bool customize_open=false) {
HEADER_GUARD { return true; }
  return false;
}
void Drain() {
  NSDate* end = [NSDate dateWithTimeIntervalSinceNow:.2];
  while (end.timeIntervalSinceNow > 0)
    [[NSRunLoop currentRunLoop] runMode:NSDefaultRunLoopMode beforeDate:end];
}
void Notify(NSNotificationName name, id object) {
  [NSNotificationCenter.defaultCenter postNotificationName:name object:object];
}
TestWindow* Window() {
  auto* w = [[TestWindow alloc] initWithContentRect:NSMakeRect(0,0,600,200)
      styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
  w.releasedWhenClosed = NO; w.testKey = YES; w.testMain = YES;
  return w;
}
void CheckActivationClick(TestApplication* app) {
  for (NSEventType type : {NSEventTypeLeftMouseDown, NSEventTypeRightMouseDown}) {
    TestWindow* parent=Window();
    TestWindow* popup=Window();
    [parent addChildWindow:popup ordered:NSWindowAbove];
    auto* pane=[[HeliumCommandPane alloc] initWithFrame:NSMakeRect(40,40,500,100)];
    [popup.contentView addSubview:pane];
    pane.input=[[HeliumNativeTextField alloc] initWithFrame:NSMakeRect(10,20,300,24)];
    [pane addSubview:pane.input];
    pane.input.stringValue=@"activation preserves query";
    assert([popup makeFirstResponder:pane.input]);
    pane.input.currentEditor.selectedRange=NSMakeRange(4,7);
    Notify(NSApplicationWillResignActiveNotification,app);
    app.testActive=NO; popup.testKey=NO;
    [popup makeFirstResponder:nil];
    auto widget=std::make_shared<Widget>(); widget->active=false;
    EventHandler handler=MakeDismissalHandler({widget},pane);
    NSEvent* activating=[NSEvent mouseEventWithType:type location:NSZeroPoint
        modifierFlags:0 timestamp:NSProcessInfo.processInfo.systemUptime
        windowNumber:parent.windowNumber context:nil eventNumber:10 clickCount:1 pressure:1];
    // The activation click is not an outside-dismissal gesture while inactive.
    assert(handler(activating)==activating);
    assert(widget->closes==0 && pane.input.preservingFocus);
    app.testActive=YES; popup.testKey=YES;
    Notify(NSApplicationDidBecomeActiveNotification,app);
    Notify(NSWindowDidBecomeKeyNotification,popup); Drain();
    assert(NSEqualRanges(pane.input.currentEditor.selectedRange,NSMakeRange(4,7)));
    // AppKit can deliver that same click after activation has already completed.
    assert(handler(activating)==activating);
    assert(widget->closes==0);
    // A fresh click after return dismisses even before Views repairs focus.
    [popup makeFirstResponder:nil]; popup.testKey=NO;
    NSEvent* next=[NSEvent mouseEventWithType:type location:NSZeroPoint
        modifierFlags:0 timestamp:NSProcessInfo.processInfo.systemUptime
        windowNumber:parent.windowNumber context:nil eventNumber:11 clickCount:1 pressure:1];
    assert(handler(next)==next); assert(widget->closes==1);
    [pane removeFromSuperview];
  }
}
void CheckAddressRingAndTransfer(TestApplication* app) {
  TestWindow* window=Window();
  auto* field=[[RingField alloc] initWithFrame:NSMakeRect(20,20,400,24)];
  field.userEditing=YES;
  field.focusSurface=window.contentView;
  field.stringValue=@"address query";
  [window.contentView addSubview:field];
  AddressOwner* owner=[[AddressOwner alloc] init];
  owner->_address=field; owner->_editing=YES; field.delegate=owner;
  __weak AddressOwner* weakSelf=owner;
TRANSFER_CALLBACK
  assert(NSEqualRects(field.focusRingMaskBounds,NSZeroRect));
  assert([window makeFirstResponder:field]); assert(field.currentEditor);
  assert(!NSEqualRects(field.focusRingMaskBounds,NSZeroRect));
  NSInteger maskChanges=field.maskChanges;
  Notify(NSApplicationWillResignActiveNotification,app);
  app.testActive=NO;
  Notify(NSApplicationDidResignActiveNotification,app);
  // App inactivity suppresses the ring even before a key-window update.
  assert(NSEqualRects(field.focusRingMaskBounds,NSZeroRect));
  window.testKey=NO;
  Notify(NSWindowDidResignKeyNotification,window);
  assert(NSEqualRects(field.focusRingMaskBounds,NSZeroRect));
  assert(field.maskChanges>maskChanges);
  assert(owner->_editing && field.preservingFocus);
  app.testActive=YES; window.testKey=YES;
  Notify(NSApplicationDidBecomeActiveNotification,app);
  Notify(NSWindowDidBecomeKeyNotification,window); Drain();
  assert(!NSEqualRects(field.focusRingMaskBounds,NSZeroRect));
  assert([field.stringValue isEqual:@"address query"]);
  // A real in-app focus transfer ends address editing rather than suspending it.
  TestWindow* popup=Window();
  [window addChildWindow:popup ordered:NSWindowAbove];
  window.testKey=NO;
  Notify(NSWindowDidResignKeyNotification,window);
  assert(NSEqualRects(field.focusRingMaskBounds,NSZeroRect));
  Notify(NSWindowDidBecomeKeyNotification,popup); Drain();
  assert(!owner->_editing && !field.currentEditor && !field.preservingFocus);
  assert(owner.finishes==1);
  assert(NSEqualRects(field.focusRingMaskBounds,NSZeroRect));
  window.testKey=YES;
  Notify(NSWindowDidBecomeKeyNotification,window); Drain();
  assert(!field.currentEditor);
  field.onFocusTransferred=nil; field.delegate=nil;
  [field removeFromSuperview];
}
int main() { @autoreleasepool {
  for (unsigned mask=0; mask<32; ++mask) {
    const bool pinned=mask&1, widget_active=mask&2, app_active=mask&4,
               command_open=mask&8, bubble_open=mask&16;
    // An active/suspended address edit retains the complete header, including
    // when both application and browser window are inactive.
    assert(!HeaderHidden(true,pinned,true,widget_active,app_active,
                         command_open,bubble_open));
    assert(HeaderHidden(false,pinned,true,widget_active,app_active,
                        command_open,bubble_open));
  }
  assert(HeaderHidden(true,false,false,false,false,false,false));
  assert(!HeaderHidden(true,false,false,true,true,false,false));
  // Preserve the existing explicit gesture/menu/customization holds.
  for (int hold=0; hold<4; ++hold)
    assert(!HeaderHidden(true,false,false,false,false,false,false,
                         hold==0,hold==1,hold==2,hold==3));
  TestApplication* app = [TestApplication sharedApplication]; app.testActive = YES;
  CheckDismissalWithoutEditor();
  CheckActivationClick(app);
  CheckAddressRingAndTransfer(app);
  TestWindow* window = Window();
  AddressOwner* owner = [[AddressOwner alloc] init];
  auto* field = [[HeliumNativeTextField alloc] init];
  field.frame = NSMakeRect(20,20,400,24);
  owner->_address = field; owner->_editing=YES; field.delegate = owner;
  field.stringValue = @"retained query";
  [window.contentView addSubview:field];
  auto widget = std::make_shared<Widget>(); WidgetAdapter adapter{widget};
  for (int i=0; i<4; ++i) {
    assert([window makeFirstResponder:field]);
    NSText* editor = field.currentEditor; assert(editor);
    editor.selectedRange = NSMakeRange(3,5);
    Notify(NSApplicationWillResignActiveNotification, app);
    assert(field.preservingFocus);
    app.testActive = NO; window.testKey = NO; widget->active = false;
    ActivationChanged(&adapter, false);
    // Chromium can replace the native responder on deactivation/reactivation.
    [window makeFirstResponder:nil]; Drain();
    assert(owner.finishes == 0); assert(widget->closes == 0);
    assert([field.stringValue isEqual:@"retained query"]);
    app.testActive = YES; window.testKey = YES; widget->active = true;
    Notify(NSApplicationDidBecomeActiveNotification, app);
    Notify(NSWindowDidBecomeKeyNotification, window);
    [window makeFirstResponder:nil]; Drain();
    assert(field.currentEditor == window.firstResponder);
    assert(NSEqualRanges(field.currentEditor.selectedRange, NSMakeRange(3,5)));
    assert(!field.preservingFocus);
  }
  // In-app responder changes still finish address editing and close Cmd-T.
  [window makeFirstResponder:nil]; widget->active = false;
  ActivationChanged(&adapter, false); Drain();
  assert(owner.finishes == 1); assert(widget->closes == 1);
  // Reactivation racing a deferred dismissal must leave an active popup open.
  ActivationChanged(&adapter, false); widget->active = true; Drain();
  assert(widget->closes == 1);
  // A window without the retained editor must not take focus on app activation.
  Notify(NSApplicationWillResignActiveNotification, app);
  Notify(NSApplicationDidBecomeActiveNotification, app); Drain();
  assert(!field.currentEditor);
  // Only the key browser window restores its editor.
  [window makeFirstResponder:field]; field.currentEditor.selectedRange=NSMakeRange(4,0);
  Notify(NSApplicationWillResignActiveNotification, app);
  [window makeFirstResponder:nil]; window.testKey=NO;
  Notify(NSApplicationDidBecomeActiveNotification, app); Drain();
  assert(!field.currentEditor);
  window.testKey=YES; Notify(NSWindowDidBecomeKeyNotification, window); Drain();
  assert(NSEqualRanges(field.currentEditor.selectedRange,NSMakeRange(4,0)));
  // Explicit cancellation prevents stale focus restoration.
  Notify(NSApplicationWillResignActiveNotification, app);
  [field cancelFocusRestoration]; [window makeFirstResponder:nil];
  Notify(NSApplicationDidBecomeActiveNotification, app); Drain();
  assert(!field.currentEditor);
  // Restore a child popup when its owning browser becomes main again.
  TestWindow* popup=Window(); popup.testKey=YES; popup.testMain=NO;
  [window addChildWindow:popup ordered:NSWindowAbove];
  [field removeFromSuperview]; [popup.contentView addSubview:field];
  field.restoresPopupKeyWindow=YES;
  assert([popup makeFirstResponder:field]); assert(field.currentEditor);
  field.currentEditor.selectedRange=NSMakeRange(2,2);
  Notify(NSApplicationWillResignActiveNotification, app);
  [popup makeFirstResponder:nil]; popup.testKey=NO;
  window.testKey=NO; window.testMain=NO;
  Notify(NSApplicationDidBecomeActiveNotification, app); Drain();
  assert(!field.currentEditor); assert(!popup.isKeyWindow);
  // The app notification can precede the browser's key/main transition.
  window.testMain=YES; window.testKey=YES;
  Notify(NSWindowDidBecomeKeyNotification, window); Drain();
  if (!field.currentEditor) fprintf(stderr,"popup restore: pending=%d parentMain=%d key=%d active=%d responder=%s finishes=%ld\n",field.preservingFocus,popup.parentWindow.isMainWindow,popup.isKeyWindow,app.isActive,[[popup.firstResponder description] UTF8String],owner.finishes);
  assert(popup.isKeyWindow); assert(field.currentEditor);
  assert(NSEqualRanges(field.currentEditor.selectedRange,NSMakeRange(2,2)));
  // Pending blocks and notifications must tolerate destroyed controls/widgets.
  ActivationChanged(&adapter,false); adapter.value.reset(); widget.reset();
  Notify(NSApplicationWillResignActiveNotification,app);
  Notify(NSApplicationDidBecomeActiveNotification,app);
  [field removeFromSuperview]; owner->_address=nil; field=nil; Drain();
  puts("PASS: native editor app-switch focus/selection, repeated cycles, activation-only first click and subsequent outside dismissal, in-app dismissal, inactive windows, parent-window popup return, header visibility, dismissal without editor focus, active-only address ring, address/palette ownership and Cmd-L handoff, cancellation and teardown");
} }
'''.replace('ADDRESS_END', address_end).replace('COMMAND_END', command_end).replace('HEADER_GUARD', guard).replace('MONITOR_HANDLER', monitor_handler).replace('ADDRESS_FIELD', address_field).replace('TRANSFER_CALLBACK', transfer)
with tempfile.TemporaryDirectory(prefix='lune-focus-retention-') as tmp:
    out = Path(tmp)
    (out/'check.mm').write_text(fixture)
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc', '-I', str(src),
                    '-arch', args.arch, '-framework', 'AppKit',
                    str(out/'check.mm'),
                    str(src/'chrome/browser/ui/views/helium/native_text_field_mac.mm'),
                    '-o', str(out/'check')], check=True)
    subprocess.run(['/usr/bin/arch', '-'+args.arch, str(out/'check')], check=True)
