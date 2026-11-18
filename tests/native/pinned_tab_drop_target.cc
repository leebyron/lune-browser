// Copyright 2026 The Lune Authors
// You can use, redistribute, and/or modify this source code under
// the terms of the GPL-3.0 license that can be found in the LICENSE file.

#include "chrome/browser/ui/views/tabs/common/pinned_tab_drop_target.h"

#include <algorithm>
#include <cassert>
#include <iostream>
#include <numeric>
#include <vector>

int main() {
  size_t cases = 0;
  for (int count = 1; count <= 12; ++count) {
    for (int columns = 1; columns <= std::min(count, 4); ++columns) {
      std::vector<PinnedTabDropCell> cells;
      const int stride = 216 / columns;
      for (int i = 0; i < count; ++i) {
        cells.push_back({i % columns * stride + stride / 2,
                         i / columns * 36 + 15});
      }
      for (int original = 0; original < count; ++original) {
        for (int destination = 0; destination < count; ++destination) {
          for (int offset : {-3, 0, 3}) {
            std::vector<int> order(count);
            std::iota(order.begin(), order.end(), 0);
            int moves = 0;
            // Keep the pointer still through repeated layout/reorder updates.
            // One move may change the model; subsequent updates must be no-ops.
            for (int update = 0; update < 120; ++update) {
              const auto source = std::find(order.begin(), order.end(), original)
                                  - order.begin();
              const auto target = PinnedTabDropInsertionTarget(
                  cells, source, cells[destination].x + offset,
                  cells[destination].y + offset);
              const int insertion = target - (source < static_cast<int>(target));
              assert(insertion == destination);
              if (source != insertion) {
                ++moves;
                order.erase(order.begin() + source);
                order.insert(order.begin() + insertion, original);
              }
            }
            assert(moves == (original != destination));
            ++cases;
          }
        }
      }
      // A partial final row should win by row even when the pointer is far
      // to the right of its final occupied cell.
      if (count % columns) {
        const int first_in_last_row = (count - 1) / columns * columns;
        const auto target = PinnedTabDropInsertionTarget(
            cells, 0, 215, cells.back().y);
        const int insertion = target - (target > 0);
        assert(insertion >= first_in_last_row);
        assert(insertion == count - 1);
      }
    }
  }
  std::cout << cases << " stable grid destinations passed, including wrapped and partial rows\n";
}
