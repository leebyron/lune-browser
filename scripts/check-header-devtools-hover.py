#!/usr/bin/env python3
"""Exercise the production header hover gate against docked DevTools layouts."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
args = parser.parse_args()
frame = args.source / 'chrome/browser/ui/views/frame'
view = (frame / 'browser_view.cc').read_text()
start = view.index('bool BrowserView::IsPointInTopChromeHoverArea(')
method = view[start:view.index('bool BrowserView::IsPointInZenTopTrigger(', start)]
# Verify both Views entry/retention paths and native entry/retention use the gate.
for name in ('IsPointInZenTopTrigger', 'IsPointInZenTopChromeBounds'):
    body = view[view.index('bool BrowserView::' + name + '('):]
    assert 'IsPointInTopChromeHoverArea(point)' in body[:250]
native = (frame / 'browser_frame_view_mac.mm').read_text()
assert 'in_hover_area = browser_view->IsPointInTopChromeHoverArea(cursor)' in native
assert 'in_rail = in_hover_area &&' in native
assert 'in_hover_area && in_window &&' in native
prefix = r'''
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <vector>
namespace gfx {
struct Point { int px, py; int x() const { return px; } };
struct Rect {
  int px=0, py=0, w=0, h=0;
  int x() const { return px; } int right() const { return px+w; }
};
}
namespace views {
struct View {
  gfx::Rect bounds; bool visible=true;
  bool GetVisible() const { return visible; }
  bool IsDrawn() const { return visible; }
  gfx::Rect GetLocalBounds() const { return {0,0,bounds.w,bounds.h}; }
  static gfx::Rect ConvertRectToTarget(const View* from, const View*, gfx::Rect r) {
    r.px+=from->bounds.px; r.py+=from->bounds.py; return r;
  }
};
}
struct ContentsContainerView : views::View {
  enum class DevToolsDockedPlacement { kLeft, kRight, kBottom, kNone, kUnknown };
  views::View devtools; gfx::Rect content;
  DevToolsDockedPlacement placement=DevToolsDockedPlacement::kNone;
  views::View* devtools_web_view() { return &devtools; }
  gfx::Rect GetContentsViewBounds() const { return content; }
  DevToolsDockedPlacement devtools_docked_placement() const { return placement; }
};
struct ContainerPtr {
  ContentsContainerView* value;
  ContentsContainerView* operator->() const { return value; }
  ContentsContainerView* get() const { return value; }
};
struct MultiContents {
  std::vector<ContainerPtr> containers;
  const auto& contents_container_views() const { return containers; }
};
struct BrowserView : views::View {
  MultiContents* multi_contents_view_; views::View* sidebar=nullptr;
  float side_ratio=0;
  views::View* GetSidebarView() const { return sidebar; }
  float GetSideChromeRevealRatio() const { return side_ratio; }
  bool IsPointInTopChromeHoverArea(const gfx::Point&) const;
};
'''
fixture = r'''
int main() {
  using Placement=ContentsContainerView::DevToolsDockedPlacement;
  ContentsContainerView first, second;
  first.bounds={216,0,984,800}; first.content={0,0,650,800};
  first.placement=Placement::kRight;
  MultiContents multi{{{&first}}}; BrowserView browser;
  browser.multi_contents_view_=&multi;
  auto allowed=[&](int x){return browser.IsPointInTopChromeHoverArea({x,0});};
  assert(allowed(216) && allowed(865) && !allowed(866) && !allowed(1199));
  // Projection must also reject DevTools above its content origin and in the
  // 48-point retention area; the enclosing reveal paths enforce height.
  assert(!browser.IsPointInTopChromeHoverArea({1000,40}));
  assert(!browser.IsPointInTopChromeHoverArea({1000,-4}));
  first.placement=Placement::kLeft; first.content={334,0,650,800};
  assert(!allowed(216) && !allowed(549) && allowed(550) && allowed(1199));
  // A detached right sidebar takes precedence over underlying DevTools.
  views::View sidebar; sidebar.bounds={984,0,216,800};
  browser.sidebar=&sidebar; browser.side_ratio=1;
  first.placement=Placement::kRight; first.content={0,0,650,800};
  assert(allowed(984) && allowed(1199) && !allowed(983));
  browser.side_ratio=0; assert(!allowed(1000));
  browser.side_ratio=1; sidebar.visible=false; assert(!allowed(1000));
  browser.sidebar=nullptr;
  // Bottom-docked and undocked tools leave the page's top span available.
  first.placement=Placement::kBottom; first.content={0,0,984,400};
  assert(allowed(216) && allowed(1199));
  first.placement=Placement::kNone; assert(allowed(1000));
  first.placement=Placement::kRight; first.content={0,0,650,800};
  first.devtools.visible=false; assert(allowed(1000));
  first.devtools.visible=true; first.visible=false; assert(allowed(1000));
  first.visible=true;
  // Every split pane uses its own local content bounds, not the active tab.
  first.bounds={216,0,450,800}; first.content={0,0,300,800};
  second.bounds={666,0,534,800}; second.content={134,0,400,800};
  second.placement=Placement::kLeft;
  multi.containers.push_back({&second});
  assert(allowed(515) && !allowed(516) && !allowed(665));
  assert(!allowed(666) && !allowed(799) && allowed(800) && allowed(1199));
  // Live resize/splitter geometry is read on every check.
  first.content.w=350; assert(allowed(550) && !allowed(566));
  // The mounted left sidebar remains eligible next to left-docked tools.
  sidebar.visible=true; sidebar.bounds={0,0,216,800}; browser.sidebar=&sidebar;
  assert(allowed(0) && allowed(215));
  puts("PASS: side-docked DevTools excluded; content, sidebar, bottom/undocked, split panes and resize preserved");
}
'''
with tempfile.TemporaryDirectory(prefix='lune-header-devtools-') as temp:
    source = Path(temp) / 'fixture.cc'
    binary = Path(temp) / 'fixture'
    source.write_text(prefix + method + fixture)
    subprocess.run(['/usr/bin/xcrun', 'clang++', '-std=c++20', '-arch', args.arch,
                    str(source), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
