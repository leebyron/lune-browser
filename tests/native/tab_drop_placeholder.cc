// Copyright 2026 The Lune Authors
// You can use, redistribute, and/or modify this source code under
// the terms of the GPL-3.0 license that can be found in the LICENSE file.

// Template for check-pinned-tab-drag.py. Production methods replace the marked
// blocks; the stubs expose only paint/entry policy and empty-layout state.

#include <algorithm>
#include <cassert>
#include <iostream>
#include <optional>
#include <vector>
namespace gfx {
struct Size { int w=0,h=0; Size()=default; Size(int a,int b):w(a),h(b){} };
struct Rect { int x=0,y=0,w=0,h=0; Rect()=default; Rect(int a,int b,int c,int d):x(a),y(b),w(c),h(d){} bool IsEmpty() const {return w<=0 || h<=0;} };
struct Canvas { int draws=0; template<class T> void DrawRoundRect(Rect,int,T){++draws;} };
}
namespace cc {struct PaintFlags {void setAntiAlias(bool){} void setColor(int){} };}
namespace ui {constexpr int kColorSysOnSurface=0;}
struct ColorProvider {int GetColor(int){return 0;}};
struct HostView {
  mutable ColorProvider colors;
  ColorProvider* GetColorProvider() const {return &colors;}
};
using SkColor = int;
namespace views {using View = HostView;}
int SkColorSetA(int color, int alpha){(void)color; return alpha;}
namespace helium {
// PRODUCTION_DROP_COLOR
}
enum class LayoutConstant {kVerticalTabCornerRadius,kTabHorizontalPadding};
int GetLayoutConstant(LayoutConstant c){return c==LayoutConstant::kTabHorizontalPadding?7:6;}
class DraggedTabsContainer {
 public:
  bool eligible=false,handling=false;
  gfx::Rect drop_placeholder_bounds_{0,0,100,30};
  HostView host; const HostView* unused=nullptr; HostView* host_view_=&host;
  bool IsHandlingDrag() const {return handling;}
  bool CanPreviewIndividualTabDrop() const {return eligible;}
  void PaintDropPlaceholder(gfx::Canvas*) const;
};
// PRODUCTION_PAINT
struct PinnedTabContainerView {
  bool eligible=false;
  enum class Orientation {kVertical,kHorizontal};
  Orientation orientation_=Orientation::kVertical;
  struct Node {std::vector<int> children; const std::vector<int>& GetDirectChildren() const{return children;}} node;
  Node* collection_node_=&node;
  struct Handler {bool dragging=false;bool IsDragging() const{return dragging;}} handler;
  const Handler& GetDragHandler() const{return handler;}
  bool CanPreviewIndividualTabDrop() const{return eligible;}
  bool HasEmptyDropEntry() const;
};
using TabStripOrientation=PinnedTabContainerView::Orientation;
// PRODUCTION_ENTRY_POLICY
namespace views {
struct ChildLayout {void* child;bool visible;gfx::Rect bounds;};
struct ProposedLayout {gfx::Size host_size;std::vector<ChildLayout> child_layouts;ChildLayout* GetLayoutFor(void* p){for(auto& c:child_layouts)if(c.child==p)return &c;return nullptr;}};
}
struct SizeBounds {std::optional<int> width() const{return 216;}};
views::ProposedLayout Layout(bool eligible) {
  (void)eligible;
  views::ProposedLayout layouts;
  const int children_on_row=0;
  // PRODUCTION_EMPTY_LAYOUT
  return layouts;
}
int main(){
  assert(helium::ChromeDropPlaceholderColor(HostView{}) == 24);
  PinnedTabContainerView policy;policy.eligible=true;
  assert(!policy.HasEmptyDropEntry());
  policy.handler.dragging=true;assert(policy.HasEmptyDropEntry());
  policy.node.children.push_back(1);assert(!policy.HasEmptyDropEntry());
  policy.node.children.clear();policy.orientation_=TabStripOrientation::kHorizontal;
  assert(!policy.HasEmptyDropEntry());
  for(int active=-1;active<3;++active){
    DraggedTabsContainer containers[3];gfx::Canvas canvas;
    for(int i=0;i<3;++i){containers[i].eligible=true;containers[i].handling=i==active;containers[i].PaintDropPlaceholder(&canvas);}
    assert(canvas.draws==(active<0?0:1));
  }
  DraggedTabsContainer cancelled;cancelled.handling=true;
  gfx::Canvas after;cancelled.PaintDropPlaceholder(&after);assert(after.draws==0);
  const auto idle=Layout(false),drag=Layout(true);
  assert(idle.host_size.h==0 && idle.host_size.w==0);
  assert(drag.host_size.h==0 && drag.host_size.w==0);
  assert(idle.child_layouts.empty() && drag.child_layouts.empty());
  std::cout<<"PASS: one active placeholder; none after cancellation; empty grid reserves no row, gap, separator, or highlighted cell\n";
}
