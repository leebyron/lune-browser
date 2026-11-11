#!/usr/bin/env python3
"""Check native toolbar symbols, semantic colors, and press-menu routing."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'))
parser.add_argument('--symbols-only', action='store_true',
                    help='Check symbol rendering and semantic colors without input fixtures')
args = parser.parse_args()
root = args.source / 'chrome/browser/ui/views/helium'
source = (root / 'native_frame_materials_mac.mm').read_text()
header = (root / 'native_frame_materials.h').read_text()
start = header.index('enum class NativeGlassColorRole')
enum = header[start:header.index('};', start) + 2]
start = source.index('\n    switch (role) {')
end = source.index('    NSColor* color =', start)
selector = 'NSColor* SelectColor(NativeGlassColorRole role) {\nNSColor* semantic=NSColor.labelColor;\n' + source[start:end] + 'return semantic;\n}\n'
start = source.index('gfx::ImageSkia NativeToolbarSymbol(')
end = source.index('\n}  // namespace helium', start)
symbol = ('gfx::ImageSkia NativeToolbarSymbolForIcon(const char*, int, SkColor);\n'
          'gfx::ImageSkia NativeToolbarSymbolForName(const char*, int, SkColor);\n' + source[start:end])
symbol_constants = (args.source / 'chrome/browser/ui/helium/helium_command_symbols.h').read_text()
symbol_constants += '\nnamespace command_symbols = helium::command_symbols;\n'
action_source = (root / 'native_frame_materials.cc').read_text()
start = action_source.index('const char* NativeToolbarSymbolNameForAction(')
end = action_source.index('\nbool IsFloatingToolbarControl(', start)
action_symbols = ('enum { kActionDevTools, kActionTaskManager, '
                  'kActionSidePanelShowCustomizeChrome, '
                  'kActionSidePanelShowCustomizeChromeToolbar };\n' +
                  action_source[start:end])
frame = (args.source / 'chrome/browser/ui/views/frame/browser_frame_view_mac.mm').read_text()
start = frame.index('@interface HeliumHeaderSymbolButton : NSButton')
button_end = frame.index('\n@end', frame.index('@implementation HeliumHeaderSymbolButton', start))
header_button = frame[start:button_end + len('\n@end')] + '\n'
start = frame.index('  NSRect address_frame = _addressContainer.frame;')
end = frame.index('  self.contentAware =', start)
address_layout = (
    'void ApplyAddressLayout(NSView* _controls, NSView* _addressContainer, '
    'NSTextField* _address, bool show_reload, bool editing) {\nconst CGFloat outset = 0;\n' +
    frame[start:end].replace('[self isEditing]', 'editing') + '}\n')
avatar_source = (args.source / 'chrome/browser/ui/views/profiles/avatar_toolbar_button.cc').read_text()
start = avatar_source.index('void AvatarToolbarButton::AnimationProgressed(')
avatar_callbacks = avatar_source[start:avatar_source.index('\nstd::optional<SkColor>', start)]
# Stand-ins isolate the AppKit calls from Chromium's Views and Skia runtime.
# Actual image masking, input and layout are checked in the browser preview.
prefix = r'''
#import <AppKit/AppKit.h>
#include <algorithm>
#include <cassert>
#include <string_view>
#include <initializer_list>
#include <optional>
#include <string>
using SkColor = unsigned;
constexpr int kNativeDownloadProgressKey = 0;
namespace views { struct View { bool floating; double GetProperty(int) const { return 0; } }; }
NSImage* NativeDownloadProgressSymbol(int, SkColor, double) { return nil; }
bool IsFloatingToolbarControl(const views::View* view) { return view->floating; }
namespace gfx {
using ImageSkia = NSImage*;
NSImage* ImageSkiaFromNSImage(NSImage* image) { return image; }
struct ImageSkiaOperations {
 static NSImage* CreateColorMask(NSImage* image, SkColor) { return image; }
};
}
'''
press_fixture = r'''
@interface ToolbarClickTarget : NSObject
@property(nonatomic) NSInteger clicks;
- (void)clicked:(id)sender;
@end
@implementation ToolbarClickTarget
- (void)clicked:(id)sender { ++_clicks; }
@end
'''
avatar_fixture = r'''
namespace gfx {
struct Animation { double value = 0; double GetCurrentValue() const { return value; } };
enum { ELIDE_TAIL };
}
#define CHECK_EQ(a, b) assert((a) == (b))
struct ToolbarButton {
  gfx::Animation hover;
  int hover_progressed = 0, hover_ended = 0;
  const gfx::Animation& hover_animation() const { return hover; }
  void AnimationProgressed(const gfx::Animation*) { ++hover_progressed; }
  void AnimationEnded(const gfx::Animation*) { ++hover_ended; }
};
struct AvatarToolbarButton : ToolbarButton {
  gfx::Animation slide_animation_;
  int size_changes = 0, text_updates = 0, highlight_updates = 0, elide_updates = 0;
  AvatarToolbarButton* label() { return this; }
  void SetElideBehavior(int) { ++elide_updates; }
  void PreferredSizeChanged() { ++size_changes; }
  void SetHighlight(std::u16string, std::nullopt_t) { ++highlight_updates; }
  void UpdateText() { ++text_updates; }
  void AnimationProgressed(const gfx::Animation*);
  void AnimationEnded(const gfx::Animation*);
};
'''
tests = r'''
int main() {
 @autoreleasepool {
  AvatarToolbarButton avatar;
  avatar.AnimationProgressed(&avatar.hover);
  avatar.AnimationEnded(&avatar.hover);
  assert(avatar.hover_progressed == 1 && avatar.hover_ended == 1);
  assert(avatar.size_changes == 0 && avatar.text_updates == 0 && avatar.elide_updates == 0);
  avatar.AnimationProgressed(&avatar.slide_animation_);
  assert(avatar.size_changes == 1 && avatar.hover_progressed == 1);
  avatar.slide_animation_.value = 1;
  avatar.AnimationEnded(&avatar.slide_animation_);
  assert(avatar.elide_updates == 1 && avatar.text_updates == 0);
  avatar.slide_animation_.value = 0;
  avatar.AnimationEnded(&avatar.slide_animation_);
  assert(avatar.elide_updates == 2 && avatar.text_updates == 1 && avatar.highlight_updates == 1);
  assert(avatar.hover_ended == 1);
  puts("PASS: production Profile callbacks separate hover and identity-pill animations");
  setbuf(stdout, nullptr);
  [NSApplication sharedApplication];
  NSView* controls = [[NSView alloc] initWithFrame:NSMakeRect(0,0,480,36)];
  NSView* container = [[NSView alloc] initWithFrame:NSMakeRect(40,8,400,20)];
  NSTextField* address = [[NSTextField alloc] initWithFrame:container.bounds];
  address.font = [NSFont systemFontOfSize:13];
  address.stringValue = @"example.com";
  ApplyAddressLayout(controls, container, address, true, false);
  assert(NSWidth(container.frame) == 400 && NSWidth(address.frame) == 400);
  ApplyAddressLayout(controls, container, address, false, false);
  assert(NSMinX(container.frame) == 40 && NSWidth(container.frame) == 432);
  assert(NSWidth(address.frame) == 400);
  address.stringValue = [@"long-address-segment/" stringByPaddingToLength:200
      withString:@"long-address-segment/" startingAtIndex:0];
  ApplyAddressLayout(controls, container, address, false, false);
  assert(NSWidth(address.frame) == 432);
  address.stringValue = @"example.com";
  ApplyAddressLayout(controls, container, address, false, true);
  assert(NSMinX(container.frame) == 40 && NSWidth(address.frame) == 432);
  ApplyAddressLayout(controls, container, address, true, true);
  assert(NSWidth(container.frame) == 400 && NSWidth(address.frame) == 400);
  puts("PASS: Reload space reclaimed for long addresses/editing; short center and leading inset stable");
  HeliumHeaderSymbolButton* button = [HeliumHeaderSymbolButton
      buttonWithImage:[NSImage imageWithSystemSymbolName:@"arrow.clockwise"
          accessibilityDescription:nil] target:nil action:nil];
  button.frame = NSMakeRect(0, 0, 32, 32);
  button.bordered = NO;
  __block int contextMenus = 0;
  button.onContextMenu = ^(NSView* sender) { ++contextMenus; };
  NSEvent* rightClick = [NSEvent mouseEventWithType:NSEventTypeRightMouseDown
      location:NSZeroPoint modifierFlags:0 timestamp:0 windowNumber:0
      context:nil eventNumber:1 clickCount:1 pressure:1];
  [button rightMouseDown:rightClick];
  assert(contextMenus == 1);
  button.enabled = NO;
  [button rightMouseDown:rightClick];
  assert(contextMenus == 1);
  button.enabled = YES;
  NSEvent* controlClick = [NSEvent mouseEventWithType:NSEventTypeLeftMouseDown
      location:NSZeroPoint modifierFlags:NSEventModifierFlagControl
      timestamp:0 windowNumber:0 context:nil eventNumber:1 clickCount:1 pressure:1];
  [button mouseDown:controlClick];
  assert(contextMenus == 2);
  puts("PASS: native right-click and Control-click routing honors enabled state");
  // Exercise AppKit's actual recognizer and NSButton event delivery.
  // Requires access to the logged-in macOS window server.
  NSWindow* window = [[NSWindow alloc] initWithContentRect:NSMakeRect(80,80,80,80)
      styleMask:NSWindowStyleMaskBorderless backing:NSBackingStoreBuffered defer:NO];
  window.releasedWhenClosed = NO;
  [window.contentView addSubview:button];
  [window orderFront:nil];
  ToolbarClickTarget* clicks = [[ToolbarClickTarget alloc] init];
  button.target = clicks;
  button.action = @selector(clicked:);
  auto send = [&](NSEventType type, NSPoint point, NSEventModifierFlags flags) {
    [NSApp postEvent:[NSEvent mouseEventWithType:type location:point
        modifierFlags:flags timestamp:NSProcessInfo.processInfo.systemUptime
        windowNumber:window.windowNumber context:nil eventNumber:1
        clickCount:1 pressure:type == NSEventTypeLeftMouseUp ? 0 : 1] atStart:NO];
  };
  auto press = [&](double duration, bool dragOut, bool disable, bool detach) {
    [NSRunLoop.mainRunLoop addTimer:[NSTimer timerWithTimeInterval:duration repeats:NO block:^(NSTimer*) {
      send(NSEventTypeLeftMouseUp, dragOut ? NSMakePoint(60,60) : NSMakePoint(16,16), 0);
    }] forMode:NSRunLoopCommonModes];
    if (dragOut || disable || detach) {
      [NSRunLoop.mainRunLoop addTimer:[NSTimer timerWithTimeInterval:.05 repeats:NO block:^(NSTimer*) {
        if (dragOut) send(NSEventTypeLeftMouseDragged, NSMakePoint(60,60), 0);
        if (disable) button.enabled = NO;
        if (detach) [button removeFromSuperview];
      }] forMode:NSRunLoopCommonModes];
    }
    send(NSEventTypeLeftMouseDown, NSMakePoint(16,16), 0);
    NSDate* end = [NSDate dateWithTimeIntervalSinceNow:duration+.15];
    while (end.timeIntervalSinceNow > 0) {
      NSEvent* event = [NSApp nextEventMatchingMask:NSEventMaskAny untilDate:end
          inMode:NSDefaultRunLoopMode dequeue:YES];
      if (event) [NSApp sendEvent:event];
    }
    printf("press %.2f drag=%d disable=%d detach=%d clicks=%ld\n",
        duration, dragOut, disable, detach, (long)clicks.clicks);
  };
  press(.05, false, false, false);
  assert(clicks.clicks == 1 && contextMenus == 2);
  press(.7, false, false, false);
  assert(clicks.clicks == 1 && contextMenus == 3);
  press(.7, true, false, false);
  assert(clicks.clicks == 1 && contextMenus == 3);
  press(.7, false, true, false);
  assert(clicks.clicks == 1 && contextMenus == 3);
  button.enabled = YES;
  press(.7, false, false, true);
  assert(clicks.clicks == 1 && contextMenus == 3);
  [window.contentView addSubview:button];
  press(.05, false, false, false);
  assert(clicks.clicks == 2 && contextMenus == 3);
  button.canShowContextMenu = ^BOOL(NSView*) { return NO; };
  press(.7, false, false, false);
  assert(clicks.clicks == 3 && contextMenus == 3);
  button.canShowContextMenu = nil;
  [button removeFromSuperview];
  [window close];
  button.onContextMenu = nil;
  puts("PASS: short click, held menu without click, drag-out, disable, detach, reuse, and unavailable-menu click fallback");
  NSImage* surface = [[NSImage alloc] initWithSize:button.frame.size];
  auto draw = [&] {
    [surface lockFocus];
    [button drawRect:button.bounds];
    [surface unlockFocus];
    return [button.contentTintColor colorUsingColorSpace:NSColorSpace.sRGBColorSpace];
  };
  auto wait = [](double seconds) {
    [NSRunLoop.mainRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:seconds]];
  };
  draw();
  [button setSymbolHovered:YES];
  wait(.04);
  double middle = [[button valueForKey:@"symbolHoverAmount"] doubleValue];
  assert(middle > 0 && middle < 1);
  // Reversing while in flight must begin at the current amount.
  [button setSymbolHovered:NO];
  double reversed = [[button valueForKey:@"symbolHoverAmount"] doubleValue];
  assert(reversed >= middle && reversed < 1);
  wait(.13);
  assert([[button valueForKey:@"symbolHoverAmount"] doubleValue] == 0);
  [button setSymbolHovered:YES];
  wait(.13);
  assert([[button valueForKey:@"symbolHoverAmount"] doubleValue] == 1);
  auto sameColor = [](NSColor* a, NSColor* b) {
    b = [b colorUsingColorSpace:NSColorSpace.sRGBColorSpace];
    printf("actual %.4f %.4f %.4f %.4f expected %.4f %.4f %.4f %.4f\n",
        a.redComponent,a.greenComponent,a.blueComponent,a.alphaComponent,
        b.redComponent,b.greenComponent,b.blueComponent,b.alphaComponent);
    return std::abs(a.redComponent-b.redComponent) < .002 &&
        std::abs(a.greenComponent-b.greenComponent) < .002 &&
        std::abs(a.blueComponent-b.blueComponent) < .002 &&
        std::abs(a.alphaComponent-b.alphaComponent) < .002;
  };
  for (NSAppearanceName name in @[NSAppearanceNameAqua,NSAppearanceNameDarkAqua]) {
    button.appearance = [NSAppearance appearanceNamed:name];
    [button.appearance performAsCurrentDrawingAppearance:^{
      assert(sameColor(draw(), SelectColor(NativeGlassColorRole::kToolbarHover)));
      button.cell.highlighted = YES;
      assert(sameColor(draw(), SelectColor(NativeGlassColorRole::kToolbarPressed)));
      button.enabled = NO;
      assert(sameColor(draw(), SelectColor(NativeGlassColorRole::kDisabledLabel)));
      button.enabled = YES;
      button.cell.highlighted = NO;
    }];
  }
  puts("PASS: native header hover fades, reversal, and semantic pressed/disabled colors");
  assert([NSImage imageWithSystemSymbolName:@"slider.horizontal.below.rectangle"
      accessibilityDescription:nil]);
  assert([NSImage imageWithSystemSymbolName:@"play.circle"
      accessibilityDescription:nil]);
  for (auto [action, name] : {
       std::pair{kActionDevTools, command_symbols::kDeveloperTools},
       std::pair{kActionTaskManager, command_symbols::kTaskManager},
       std::pair{kActionSidePanelShowCustomizeChrome, command_symbols::kCustomizeAppearance},
       std::pair{kActionSidePanelShowCustomizeChromeToolbar, command_symbols::kCustomizeToolbar}}) {
    assert(std::string_view(NativeToolbarSymbolNameForAction(action)) == name);
    assert(NativeToolbarSymbolForName(name, 20, 0));
  }
  assert(!NativeToolbarSymbolNameForAction(-1));
  assert(NativeToolbarSymbolForName(command_symbols::kPinToolbar, 20, 0));
  assert(NativeToolbarSymbolForName(command_symbols::kSidebarLeft, 20, 0));
  assert(NativeToolbarSymbolForName(command_symbols::kSidebarRight, 20, 0));
  views::View view{true};
  for (auto name : {"kMoreVertIcon", "kChromeExtensionIcon", "kDownloadIcon",
                    "kPrintIcon", "kHistoryIcon", "kTranslateIcon", "kShareIcon",
                    "kSplitSceneIcon", "kSplitSceneOldIcon", "kHotelClassIcon",
                    "kDeleteIcon", "kCastIcon", "kQrCodeIcon", "kCodeIcon",
                    "kTableChartIcon", "kLinkIcon", "kEditIcon", "kAccountBoxIcon",
                    "kQueueMusicIcon", "kAccountCircleIcon", "kManageSearchIcon",
                    "kMediaToolbarButtonChromeRefreshOldIcon",
                    "kMediaToolbarButtonTouchOldIcon",
                    "kTabSearchTabStripOldIcon", "kIncognitoIcon",
                    "kIncognitoRefreshMenuOldIcon", "kHomeIcon", "kAddIcon", "kGlobeIcon",
                    "kArrowBackIcon", "kArrowForwardIcon", "kRefreshIcon",
                    "kSidebarLeftIcon", "kSidebarRightIcon"}) {
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
  assert(!NativeToolbarSymbol(&view,nullptr,20,0));
  assert(!NativeToolbarSymbolForIcon(nullptr,20,0));
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
if args.symbols_only:
    tests = ('int main() { @autoreleasepool {\n' +
             tests[tests.index('  assert([NSImage imageWithSystemSymbolName:'):])
with tempfile.TemporaryDirectory(prefix='lune-toolbar-') as directory:
    path = Path(directory) / 'test.mm'
    path.write_text(prefix + symbol_constants + action_symbols + enum + selector + symbol + header_button + address_layout +
                    press_fixture + avatar_fixture + avatar_callbacks + tests)
    binary = path.with_suffix('')
    subprocess.run(['xcrun', 'clang++', *(['-arch', args.arch] if args.arch else []),
                    '-std=c++20', '-fobjc-arc', '-framework', 'AppKit', str(path),
                    '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True, timeout=30)
