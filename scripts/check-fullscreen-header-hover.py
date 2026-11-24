#!/usr/bin/env python3
"""Exercise production native hover and fullscreen menu-bar geometry."""

import argparse
from pathlib import Path
import re
import subprocess
import tempfile


def check(source, arch):
    views = source / 'chrome/browser/ui/views'
    native = (views / 'helium/native_frame_materials_mac.mm').read_text()
    start = native.index('int NativeFullscreenTopControlsOffset(')
    methods = native[start:native.index('\n}  // namespace helium', start)]
    header = (views / 'helium/native_frame_materials.h').read_text()
    constants = '\n'.join(re.findall(
        r'inline constexpr int kNative(?:(?:Top|Side)Chrome'
        r'(?:Reveal|Retention)Distance|Toolbar(?:ControlHeight|VerticalPadding)) = \d+;',
        header))
    assert len(constants.splitlines()) == 6
    geometry = '\n'.join(re.findall(
        r'inline constexpr bool Is(?:WithinNativeTopChromeRetention|InNativeSidebarTopHoverColumn)'
        r'\([^}]+}', header))
    frame = (views / 'frame/browser_frame_view_mac.mm').read_text()
    retention = re.search(r'  const bool within_retention = .*?;', frame, re.S)[0]
    sidebar_header = re.search(r'  const bool in_sidebar_header = .*?;', frame, re.S)[0]
    above = re.search(r'  const bool above_sidebar_header = .*?;', frame, re.S)[0]
    reveal = re.search(r'  const bool in_rail = .*?;', frame, re.S)[0]
    in_window = re.search(r'  const bool in_window =.*?;', frame, re.S)[0]
    pointer_decision = '\n'.join([
        sidebar_header, above, reveal, in_window, retention])
    assert 'helium::IsPointerAboveNativeFullscreenContent(' in frame
    assert 'helium::NativeFullscreenTopControlsOffset(' in frame
    view = (views / 'frame/browser_view.cc').read_text()
    gap = view[view.index('  const bool has_cursor ='):]
    gap = gap[:gap.index('  bool in_hover_window')]
    assert 'IsPointerAboveNativeFullscreenContent(' in gap
    assert 'GetFrameView()->GetFloatingChromeTopOffset()' in gap
    assert 'zen_cursor_exit_timer_.Stop()' in gap
    assert re.search(r'UpdateZenModeReveal\(IsPointInZenTopTrigger\(cursor\),\s+'
                     r'IsPointInZenSideTrigger\(cursor\)\)', gap)
    assert 'helium::IsPointerInNativeWindowHoverArea(this, true)' in view
    assert 'poll_cursor &= GetWidget()->IsActive()' in view
    sidebar = frame[frame.index('void BrowserFrameViewMac::UpdateFloatingSidebar('):]
    assert '!fullscreen_utils::IsInContentFullscreen(view->browser())' in sidebar[:450]
    eligibility = view[view.index('bool BrowserView::ShouldDrawVerticalTabStrip()'):]
    eligibility = eligibility[:eligibility.index('\nbool BrowserView::')]
    side_trigger = re.search(
        r'bool BrowserView::IsPointInZenSideTrigger\([^\n]+\n.*?\n}', view, re.S)[0]
    old_trigger_width = re.search(r'constexpr int kZenModeRevealTriggerThickness = \d+;',
                                  view)[0]
    side_retention = re.search(
        r'    within_side_retention = IsVerticalTabStripRightAligned\(\).*?;',
        view, re.S)[0]
    assert 'retention_distance = helium::kNativeSideChromeRetentionDistance' in view
    top_side_retention = re.search(
        r'      const int toolbar_bottom = .*?within_side_retention \|=.*?;',
        view, re.S)[0]

    fixture = r'''
#import <Cocoa/Cocoa.h>
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <initializer_list>
#define BUILDFLAG(x) 1
struct BrowserView;
namespace gfx {
struct Point {
  int px, py = 0;
  int x() const { return px; }
  int y() const { return py; }
};
struct Rect {
  int left, top, width, height;
  int x() const { return left; }
  int y() const { return top; }
  int right() const { return left + width; }
  bool Contains(const Point& p) const {
    return p.x() >= x() && p.x() < right() &&
           p.y() >= y() && p.y() < y() + height;
  }
};
}
struct BrowserWindowInterface { enum class Type { TYPE_NORMAL, TYPE_POPUP }; };
namespace tabs {
struct VerticalTabStripStateController {
  bool vertical=true;
  bool ShouldDisplayVerticalTabs() const { return vertical; }
  bool IsTabStripRightAligned() const { return false; }
  static VerticalTabStripStateController* From(const BrowserView*);
};
static VerticalTabStripStateController controller;
VerticalTabStripStateController* VerticalTabStripStateController::From(const BrowserView*) {
  return &controller;
}
}
static NSPoint pointer;
@interface TestEvent : NSObject
+ (NSPoint)mouseLocation;
@end
@implementation TestEvent
+ (NSPoint)mouseLocation { return pointer; }
@end
@interface TestMenu : NSObject
@property CGFloat menuBarHeight;
@end
@implementation TestMenu
@end
@interface TestApplication : NSObject
@property(strong) TestMenu* mainMenu;
+ (instancetype)sharedApplication;
@end
static TestApplication* application;
@implementation TestApplication
+ (instancetype)sharedApplication { return application; }
@end
@interface TestScreen : NSObject
@property NSRect frame;
@end
@implementation TestScreen
@end
@interface TestContent : NSObject
@property NSRect bounds;
@property BOOL isFlipped;
- (NSRect)convertRect:(NSRect)r toView:(id)view;
- (NSPoint)convertPoint:(NSPoint)p fromView:(id)view;
@end
@implementation TestContent
- (NSRect)convertRect:(NSRect)r toView:(id)view { return r; }
- (NSPoint)convertPoint:(NSPoint)p fromView:(id)view { return p; }
@end
@interface TestWindow : NSObject
@property(strong) TestScreen* screen;
@property(strong) TestContent* contentView;
@property CGFloat backingScaleFactor;
@property NSPoint origin;
- (NSRect)convertRectToScreen:(NSRect)r;
- (NSPoint)convertPointFromScreen:(NSPoint)p;
@end
@implementation TestWindow
- (NSRect)convertRectToScreen:(NSRect)r {
  return NSOffsetRect(r, self.origin.x, self.origin.y);
}
- (NSPoint)convertPointFromScreen:(NSPoint)p {
  return NSMakePoint(p.x-self.origin.x, p.y-self.origin.y);
}
@end
struct NativeWindow {
  TestWindow* window;
  NSWindow* GetNativeNSWindow() const { return (NSWindow*)window; }
};
struct Widget {
  TestWindow* window;
  NativeWindow GetNativeWindow() const { return {window}; }
};
struct FrameView {
  int offset = 0;
  bool HasFloatingAddressBar() const { return true; }
  int GetFloatingChromeTopOffset() const { return offset; }
};
struct BrowserView {
  Widget* widget;
  bool fullscreen=true, content_fullscreen=false, right=false, tabstrip=true;
  BrowserWindowInterface::Type type=BrowserWindowInterface::Type::TYPE_NORMAL;
  FrameView frame;
  const BrowserView* browser_=this;
  bool top_hover = true;
  bool IsTopChromeHoverEnabled() const { return top_hover; }
  gfx::Rect GetLocalBounds() const {
    return {0, 0, width(), static_cast<int>(widget->window.contentView.bounds.size.height)};
  }
  Widget* GetWidget() const { return widget; }
  bool IsFullscreen() const { return fullscreen; }
  const BrowserView* browser() const { return this; }
  bool IsVerticalTabStripRightAligned() const { return right; }
  bool ShouldDrawTabStrip() const { return tabstrip; }
  const FrameView* GetFrameView() const { return &frame; }
  int width() const { return 1920; }
  BrowserWindowInterface::Type GetType() const { return type; }
  bool ShouldDrawVerticalTabStrip() const;
  bool IsPointInZenSideTrigger(const gfx::Point& point) const;
};
namespace fullscreen_utils {
bool IsInContentFullscreen(const BrowserView* view) { return view->content_fullscreen; }
}
#define NSEvent TestEvent
#define NSApplication TestApplication
namespace helium {
''' + constants + '\n' + geometry + '\n' + methods + r'''
}
#undef NSApplication
#undef NSEvent
using namespace helium;
''' + eligibility + old_trigger_width + '\n' + side_trigger + r'''
@interface TestBar : NSObject
@property BOOL isPresented;
@end
@implementation TestBar
@end
struct TestPoint { int py; int y() const { return py; } };
struct TestRect { int b; int bottom() const { return b; } };
bool Retained(bool presented, bool in_hover_area, bool in_window, int y, int bottom) {
  TestBar* floating_address_bar_ = [TestBar new];
  floating_address_bar_.isPresented=presented;
  TestPoint cursor{y}; TestRect bounds{bottom};
''' + retention + r'''
  return within_retention;
}
bool PointerShowsToolbar(BrowserView* browser_view, gfx::Point cursor,
                         const gfx::Rect& sidebar_header, bool in_hover_area,
                         bool already_presented, int offset) {
  TestBar* floating_address_bar_ = [TestBar new];
  floating_address_bar_.isPresented = already_presented;
  TestRect bounds{44 + offset};
  const auto TopUIFullscreenYOffset = [&] { return offset; };
''' + pointer_decision + r'''
  return in_rail || in_sidebar_header || within_retention;
}
bool SideRetained(bool right, int x, int left, int end) {
  struct SidePoint { int value; int x() const { return value; } } cursor{x};
  struct SideBounds {
    int left,end; int x() const { return left; } int right() const { return end; }
  } sidebar{left,end};
  const auto IsVerticalTabStripRightAligned=[&] { return right; };
  int retention_distance=helium::kNativeSideChromeRetentionDistance;
  bool within_side_retention=false;
''' + side_retention + r'''
  return within_side_retention;
}
bool SidebarTopRetained(bool right, int x, int y, int offset) {
  struct Point { int px, py; int x() const { return px; } int y() const { return py; } };
  const Point cursor{x, y};
  const FrameView browser_frame{offset};
  const FrameView* frame = &browser_frame;
  const auto IsVerticalTabStripRightAligned = [&] { return right; };
  const auto width = [] { return 1920; };
  bool within_side_retention = false;
''' + top_side_retention + r'''
  return within_side_retention;
}
int main() { @autoreleasepool {
  application=[TestApplication new]; application.mainMenu=[TestMenu new];
  TestScreen* screen=[TestScreen new]; TestContent* content=[TestContent new];
  TestWindow* window=[TestWindow new]; window.screen=screen; window.contentView=content;
  Widget widget{window}; BrowserView view{&widget};
  assert(NativeFullscreenTopControlsOffset(nullptr,1)==0);
  assert(!IsPointerAboveNativeFullscreenContent(nullptr,0));
  for (NSPoint origin : {NSMakePoint(0,0),NSMakePoint(-1920,200),NSMakePoint(0,-1080)}) {
    screen.frame=NSMakeRect(origin.x,origin.y,1920,1080); window.origin=origin;
    const CGFloat screen_top=NSMaxY(screen.frame);
    for (CGFloat scale : {1.,2.}) {
      window.backingScaleFactor=scale;
      for (bool page : {false,true}) {
        view.fullscreen=true; view.content_fullscreen=page;
        for (CGFloat native_gap : {0.,24.,30.,38.,74.}) {
          content.bounds=NSMakeRect(0,0,1920,1080-native_gap);
          for (CGFloat height : {24.,30.,38.}) {
            application.mainMenu.menuBarHeight=height;
            // Initial fullscreen, menu animation in/out, and a changed setting.
            for (double fraction : {0.,.25,.5,1.,.5,.25,0.,1.}) {
              int offset=NativeFullscreenTopControlsOffset(&view,fraction);
              CGFloat menu_bottom=screen_top-height*fraction;
              CGFloat native_top=screen_top-native_gap;
              CGFloat available_top=native_top-offset;
              if (native_top<=menu_bottom) assert(offset==0);
              else assert(available_top<=menu_bottom && menu_bottom<available_top+1);
              CGFloat gap=screen_top-available_top;
              CGFloat thickness=gap>0?1/scale:4;
              view.frame.offset=offset;
              for (CGFloat distance : {-1.,0.,gap/2,gap,gap+thickness,
                                        gap+thickness+.25,gap+108,gap+109}) {
                pointer=NSMakePoint(origin.x+800,screen_top-distance);
                bool above=distance>=0 && distance<=gap;
                assert(IsPointerAboveNativeFullscreenContent(&view,offset)==above);
                assert(IsPointerInNativeRevealRail(&view,true,offset)==
                       (distance>=0 && distance<=gap+thickness));
                int local_y=static_cast<int>(std::floor(distance-native_gap));
                bool in_window=local_y>=0 && local_y<1080-native_gap;
                assert(Retained(true,true,in_window||above,local_y,44+offset)==
                       (distance>=0 && local_y<=108+offset));
                assert(!Retained(true,false,in_window||above,local_y,44+offset));
                assert(!Retained(false,true,in_window||above,local_y,44+offset));
                for (bool right : {false,true}) {
                  view.right=right;
                  for (int x : {111,112,1807,1808}) {
                    pointer.x=origin.x+x;
                    assert(view.IsPointInZenSideTrigger({x}) ==
                           (!page && (right ? x>=1808 : x<112) &&
                            distance>=0 && distance<=gap+thickness));
                  }
                }
              }
              pointer=NSMakePoint(origin.x-1,screen_top-1);
              assert(!IsPointerInNativeRevealRail(&view,true,offset));
              assert(!IsPointerAboveNativeFullscreenContent(&view,offset));
              pointer.x=origin.x+1920;
              assert(!IsPointerInNativeRevealRail(&view,true,offset));
            }
          }
        }
        content.bounds=NSMakeRect(0,0,1920,1080);
        for (bool right : {false,true}) {
          view.right=right;
          pointer=NSMakePoint(origin.x+(right?1904:15.5),origin.y+500);
          assert(IsPointerInNativeRevealRail(&view,false,0)==!page);
          pointer.x=origin.x+(right?1903.5:16);
          assert(!IsPointerInNativeRevealRail(&view,false,0));
        }
      }
      view.fullscreen=false; view.content_fullscreen=false;
      content.bounds=NSMakeRect(0,0,1920,1080);
      for (CGFloat x : {-129.,-128.,-127.,-17.,-16.,-15.,0.,1920.,1935.,1936.,1937.,2048.,2049.}) {
        pointer=NSMakePoint(origin.x+x,origin.y+500);
        assert(IsPointerInNativeWindowHoverArea(&view,false)==(x>=-16 && x<=1936));
        assert(IsPointerInNativeWindowHoverArea(&view,true)==(x>=-128 && x<=2048));
      }
      for (CGFloat y : {-65.,-64.,-63.,-17.,-16.,-15.,0.,1080.,1095.,1096.,1097.,1143.,1144.,1145.}) {
        pointer=NSMakePoint(origin.x+800,origin.y+y);
        assert(IsPointerInNativeWindowHoverArea(&view,false)==(y>=-16 && y<=1096));
        assert(IsPointerInNativeWindowHoverArea(&view,true)==(y>=-64 && y<=1144));
      }
      for (bool right : {false,true}) {
        view.right=right;
        pointer=NSMakePoint(origin.x+(right?1904:15.5),origin.y+500);
        assert(IsPointerInNativeRevealRail(&view,false,0));
        pointer.x=origin.x+(right?1903.5:16);
        assert(!IsPointerInNativeRevealRail(&view,false,0));
      }
      for (CGFloat depth : {-17.,-16.,0.,3.,3.5,4.,4.5,7.5,8.,16.}) {
        pointer=NSMakePoint(origin.x+800,origin.y+1080-depth);
        assert(IsPointerInNativeRevealRail(&view,true,0)==
               (depth>=-16 && depth<4));
        for (bool right : {false,true}) {
          view.right=right;
          for (int x : {111,112,1807,1808}) {
            pointer.x=origin.x+x;
            assert(view.IsPointInZenSideTrigger({x}) ==
                   ((right ? x>=1808 : x<112) && depth>=-16 && depth<4));
          }
        }
      }
      const int left_sidebar_width = 216;
      const int right_sidebar_start = 1704;
      for (bool right : {false, true}) {
        const int sidebar_x = right ? right_sidebar_start + 70 : 70;
        const int boundary_x = right ? right_sidebar_start : left_sidebar_width - 1;
        const int page_x = right ? right_sidebar_start - 1 : left_sidebar_width;
        view.top_hover = false;
        for (int header_y : {0,8}) {
          const gfx::Rect sidebar = right ?
              gfx::Rect{right_sidebar_start, header_y, 216, 52} :
              gfx::Rect{0, header_y, 216, 52};
          for (int x : {sidebar_x, boundary_x, page_x, 960}) {
            bool in_column = x == sidebar_x || x == boundary_x;
            for (int depth : {-65,-64,-17,-16,-1,0,3,4,7,10,51,60,108,109}) {
              pointer = NSMakePoint(origin.x + x, origin.y + 1080 - depth);
              const bool in_header = in_column && depth >= header_y &&
                                     depth < header_y + 52;
              const bool sidebar_entry = in_header ||
                  (in_column && depth >= -16 && depth < 4 && depth < header_y);
              const bool retained = depth >= -64 && depth <= 108;
              assert(PointerShowsToolbar(&view,{x,depth},sidebar,true,false,0) ==
                     sidebar_entry);
              assert(PointerShowsToolbar(&view,{x,depth},sidebar,true,true,0) ==
                     (sidebar_entry || retained));
              assert(!PointerShowsToolbar(&view,{x,depth},{},true,false,0));
              if (!in_column)
                assert(!PointerShowsToolbar(&view,{x,depth},sidebar,false,true,0));
            }
          }
          view.top_hover = true;
          pointer = NSMakePoint(origin.x + page_x, origin.y + 1080 + 16);
          assert(PointerShowsToolbar(&view,{page_x,-16},sidebar,true,false,0));
          for (int depth : {3,4,5,7}) {
            pointer = NSMakePoint(origin.x + page_x, origin.y + 1080 - depth);
            assert(PointerShowsToolbar(&view,{page_x,depth},sidebar,true,false,0) ==
                   (depth < 4));
          }
          view.top_hover = false;
        }
        view.fullscreen = true;
        content.bounds = NSMakeRect(0,0,1920,1050);
        const gfx::Rect sidebar = right ?
            gfx::Rect{right_sidebar_start,0,216,52} : gfx::Rect{0,0,216,52};
        pointer = NSMakePoint(origin.x + sidebar_x, origin.y + 1070);
        assert(PointerShowsToolbar(&view,{sidebar_x,-20},sidebar,true,false,0));
        pointer.x = origin.x + page_x;
        assert(!PointerShowsToolbar(&view,{page_x,-20},sidebar,true,false,0));
        content.bounds = NSMakeRect(0,0,1920,1080);
        view.fullscreen = false;
      }
      view.top_hover = true;
      assert(NativeFullscreenTopControlsOffset(&view,1)==0);
      assert(!IsPointerAboveNativeFullscreenContent(&view,0));
    }
  }
  // Moving the native window below an always-visible menu must not add the
  // same inset a second time: both initial and settled states align equally.
  view.fullscreen=true; application.mainMenu.menuBarHeight=30;
  content.bounds=NSMakeRect(0,0,1920,1080);
  assert(NativeFullscreenTopControlsOffset(&view,1)==30);
  content.bounds=NSMakeRect(0,0,1920,1050);
  assert(NativeFullscreenTopControlsOffset(&view,1)==0);
  assert(Retained(true,true,true,108,44));
  assert(!Retained(true,true,true,109,44));
  assert(SideRetained(false,344,0,216));
  assert(!SideRetained(false,345,0,216));
  assert(SideRetained(true,1576,1704,1920));
  assert(!SideRetained(true,1575,1704,1920));
  for (int offset : {0,30}) {
    assert(SidebarTopRetained(false,111,108+offset,offset));
    assert(SidebarTopRetained(true,1808,108+offset,offset));
    assert(!SidebarTopRetained(false,111,109+offset,offset));
    assert(!SidebarTopRetained(true,1808,109+offset,offset));
    assert(!SidebarTopRetained(false,112,108+offset,offset));
    assert(!SidebarTopRetained(true,1807,108+offset,offset));
  }
  for (bool fullscreen : {false,true}) for (bool page : {false,true}) {
    view.fullscreen=fullscreen; view.content_fullscreen=page;
    assert(view.ShouldDrawVerticalTabStrip()==!page);
  }
  view.content_fullscreen=false; view.tabstrip=false;
  assert(!view.ShouldDrawVerticalTabStrip());
  view.tabstrip=true; tabs::controller.vertical=false;
  assert(!view.ShouldDrawVerticalTabStrip());
  tabs::controller.vertical=true; view.type=BrowserWindowInterface::Type::TYPE_POPUP;
  assert(!view.ShouldDrawVerticalTabStrip());
  puts("PASS: sidebar header entry and retention on either side in both hover modes, top entry 4 inside and 16 outside, top retention 64, sidebar top entry 112 on either side, side 16/128, fullscreen menus, display origins and scales");
} }
'''
    with tempfile.TemporaryDirectory(prefix='lune-fullscreen-hover-') as temp:
        code, binary = Path(temp) / 'fixture.mm', Path(temp) / 'fixture'
        code.write_text(fixture)
        subprocess.run(['/usr/bin/xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                        '-arch', arch, '-framework', 'Cocoa', str(code), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
    args = parser.parse_args()
    check(args.source, args.arch)
