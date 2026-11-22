// SPDX-License-Identifier: MIT
// The check script fills the marked statements from prepared Chromium.

#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>

#define BUILDFLAG(flag) 0

namespace gfx {
struct Size {
  int w, h;
  int width() const { return w; }
  int height() const { return h; }
};

struct Rect {
  int x, y, width, height;
};

class Tween {
 public:
  static int IntValueBetween(double value, int start, int target);
};
// PRODUCTION_TWEEN
}

enum class LayoutConstant { kVerticalTabHeight, kVerticalTabPinnedHeight };

int RowHeight(LayoutConstant constant, bool spacious) {
  switch (constant) {
    // PRODUCTION_ROW_HEIGHTS
  }
  std::abort();
}

struct TabView {
  bool pinned_;
  bool dragging = true;
  double pin_drag_start_progress_;
  double progress;
  gfx::Size pin_drag_start_size_;

  bool IsPinDragAnimating() const { return true; }
  bool IsDragging() const { return dragging; }
  double GetPinDragProgress() const { return progress; }
  double GetPinDragTransitionProgress() const;
  gfx::Size GetPinDragSize(const gfx::Size& target) const;
};
// PRODUCTION_TRANSITION

gfx::Rect FloatingBounds(const gfx::Size* observed_view, double ratio) {
  struct Ratios {
    double y_value;
    double x() const { return 0.5; }
    double y() const { return y_value; }
  };
  const struct {
    Ratios mouse_offset_to_size_ratios;
  } session{{ratio}};
  gfx::Rect dragging_views_bounds_;
  // PRODUCTION_FLOATING_BOUNDS
  return dragging_views_bounds_;
}

int main() {
  for (bool comfortable : {false, true}) {
    const int regular = RowHeight(LayoutConstant::kVerticalTabHeight, comfortable);
    const int pinned = RowHeight(LayoutConstant::kVerticalTabPinnedHeight, comfortable);
    assert(regular == (comfortable ? 36 : 30));
    assert(pinned == (comfortable ? 46 : 36));

    const gfx::Size row{240, regular}, tile{100, pinned};
    for (double ratio : {0.2, 0.5, 0.8}) {
      const int row_offset = FloatingBounds(&row, ratio).y;
      const int tile_offset = FloatingBounds(&tile, ratio).y;
      assert(std::abs(row_offset - tile_offset - ratio * (pinned - regular)) < 1);

      TabView drag{true, true, 0.0, 0.0, row};
      int previous_height = regular;
      for (int frame = 0; frame <= 100; ++frame) {
        drag.progress = frame / 100.0;
        const gfx::Size size = drag.GetPinDragSize(tile);
        const gfx::Rect bounds = FloatingBounds(&size, ratio);
        assert(size.height() >= previous_height && size.height() <= pinned);
        assert(bounds.height == size.height());
        assert(std::abs(-bounds.y - ratio * size.height()) < 1);
        previous_height = size.height();
      }

      drag.progress = 0.4;
      const gfx::Size before_reverse = drag.GetPinDragSize(tile);
      const gfx::Rect before_bounds = FloatingBounds(&before_reverse, ratio);
      drag = TabView{false, true, 0.4, 0.4, before_reverse};
      const gfx::Size after_reverse = drag.GetPinDragSize(row);
      assert(after_reverse.height() == before_reverse.height());
      assert(FloatingBounds(&after_reverse, ratio).y == before_bounds.y);
      drag.progress = 0.0;
      assert(drag.GetPinDragSize(row).height() == regular);

      drag = TabView{true, true, 0.0, 0.4, row};
      drag.dragging = false;
      assert(drag.GetPinDragSize(tile).height() == pinned);
    }
  }
  puts("PASS: both densities, off-center cursor anchoring, reversal, and early drop");
}
