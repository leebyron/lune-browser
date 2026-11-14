#!/usr/bin/env python3
"""Exercise production Older Tabs drag clock methods with isolated model stubs.

This runs the actual FinishDrag/Interact/ReturnToRegular bodies. It checks clock
semantics, not native pointer delivery, model ordering, or session persistence;
check-older-tabs.py covers the real browser/model and saved-session paths.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import tempfile


def function(source, signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        if source[end] == "{":
            depth += 1
        elif source[end] == "}":
            depth -= 1
        end += 1
    return source[start:end]


PREFIX = r'''
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <optional>
#include <stdexcept>
#include <tuple>
#include <vector>
namespace base {
int64_t now = 1000000;
struct Time {
  int64_t value = 0;
  static Time Now() { return {now}; }
  bool is_null() const { return value == 0; }
  bool operator==(const Time&) const = default;
};
int64_t operator-(Time a, Time b) { return a.value - b.value; }
using TimeTicks = Time;
int64_t Seconds(int n) { return n; }
}
struct CleanupData {
  base::Time age{100}, last_use{90}, close_clock, frozen, last_saved;
  double order = 0;
  std::optional<double> drag_original_order;
  int drag_origin_window = 0;
  bool drag_regular = false, dragging = false, dirty = false;
};
namespace content { struct WebContents { CleanupData data; }; }
CleanupData& Get(content::WebContents* c) { return c->data; }
struct TabDragController {
  static bool active;
  static bool IsActive() { return active; }
};
bool TabDragController::active = false;
struct SessionId { int id() const { return 1; } };
struct Browser { SessionId GetSessionID() const { return {}; } };
struct Delegate {
  Browser browser;
  Browser* GetBrowserWindowInterface() { return &browser; }
};
struct TabStripModel {
  static constexpr int kNoTab = -1;
  std::vector<content::WebContents*> tabs;
  Delegate delegate_;
  Delegate* delegate() { return &delegate_; }
  int GetIndexOfWebContents(content::WebContents* tab) const {
    auto it = std::find(tabs.begin(), tabs.end(), tab);
    return it == tabs.end() ? kNoTab : int(it - tabs.begin());
  }
};
class OlderTabsController {
 public:
  explicit OlderTabsController(TabStripModel* model) : model_(model) {}
  void FinishDrag(const std::vector<content::WebContents*>&, bool);
  void Interact(content::WebContents*);
  static bool IsOlder(content::WebContents* tab) {
    return !Get(tab).close_clock.is_null();
  }
  void AssignOrder(content::WebContents* tab) {
    Get(tab).order = model_->GetIndexOfWebContents(tab) + 0.5;
    Save(tab);
  }
  void Save(content::WebContents* tab) {
    Get(tab).last_saved = base::TimeTicks::Now();
  }
  void ScheduleReconcile() {}
 private:
  TabStripModel* model_;
};
auto Clocks(content::WebContents* tab) {
  const auto& d = Get(tab);
  return std::make_tuple(d.age, d.last_use, d.close_clock, d.frozen);
}
void Check(bool value, const char* message) {
  if (!value) throw std::runtime_error(message);
}
'''

CASES = r'''
int main() {
 try {
  content::WebContents storage[13];
  TabStripModel model;
  for (auto& tab : storage) model.tabs.push_back(&tab);
  OlderTabsController controller(&model);
  const auto before = Clocks(&storage[0]);
  controller.FinishDrag(model.tabs, true);
  for (auto* tab : model.tabs)
    Check(Clocks(tab) == before, "completed no-op/batch drag refreshed a regular tab");
  std::reverse(model.tabs.begin(), model.tabs.end());
  controller.FinishDrag(model.tabs, true);
  for (auto* tab : model.tabs)
    Check(Clocks(tab) == before, "completed reordered drag refreshed a regular tab");
  controller.FinishDrag(model.tabs, false);
  for (auto* tab : model.tabs)
    Check(Clocks(tab) == before, "cancelled regular drag refreshed a tab");

  auto* older = &storage[0];
  Get(older).close_clock = {200};
  Get(older).frozen = {90};
  Get(older).drag_original_order = Get(older).order;
  Get(older).drag_origin_window = 1;
  Get(older).dragging = true;
  const auto older_before = Clocks(older);
  controller.FinishDrag({older}, true);
  Check(Clocks(older) == older_before, "drop within Older changed its clocks");
  Check(OlderTabsController::IsOlder(older), "drop within Older kept a tab");
  Get(older).drag_regular = true;
  controller.FinishDrag({older}, false);
  Check(Clocks(older) == older_before, "cancelled crossing out of Older kept a tab");
  Get(older).drag_regular = true;
  controller.FinishDrag({older}, true);
  Check(!OlderTabsController::IsOlder(older), "deliberate drag out of Older did not Keep");
  Check(Get(older).age == base::Time::Now(), "Keep did not start a fresh countdown");
  Check(Get(older).last_use.value == 90, "Keep changed historical last use");
  Check(Get(older).frozen.is_null(), "Keep retained a frozen date");

  auto* regular = &storage[1];
  controller.Interact(regular);
  Check(Get(regular).age == base::Time::Now(), "regular page use did not reset inactivity");
  Check(Get(regular).last_use == base::Time::Now(), "regular page use did not update last use");
  Get(older).close_clock = {200};
  Get(older).frozen = {90};
  const auto saved_age = Get(older).age;
  ++base::now;
  controller.Interact(older);
  Check(Get(older).age == saved_age, "Older interaction reset its regular-age baseline");
  Check(Get(older).close_clock == base::Time::Now(), "Older interaction did not extend retention");
  Check(Get(older).frozen.value == 90, "Older interaction changed its date bucket");

  content::WebContents detached;
  const auto detached_before = Clocks(&detached);
  controller.FinishDrag({&detached}, true);
  Check(Clocks(&detached) == detached_before, "foreign tab was changed");
  puts("PASS: 13-tab no-op/reordered/cancelled drags preserve clocks; Older placement/cancel/Keep and real interaction rules pass");
  return 0;
 } catch (const std::exception& error) {
  fprintf(stderr, "FAIL: %s\n", error.what());
  return 1;
 }
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--arch", choices=("arm64", "x86_64"), required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expect-failure", action="store_true")
    args = parser.parse_args()
    source = (args.source / "chrome/browser/ui/tabs/older_tabs_controller.cc").read_text()
    methods = [function(source, signature) for signature in (
        "void ReturnToRegular(", "void OlderTabsController::FinishDrag(",
        "void OlderTabsController::Interact(")]
    with tempfile.TemporaryDirectory(prefix="lune-older-arrangement-") as temporary:
        path = Path(temporary)
        (path / "check.cc").write_text(PREFIX + "\n".join(methods) + CASES)
        subprocess.run(["xcrun", "clang++", "-std=c++20", "-arch", args.arch,
                        str(path / "check.cc"), "-o", str(path / "check")], check=True)
        result = subprocess.run(["/usr/bin/arch", "-" + args.arch, str(path / "check")],
                                capture_output=True, text=True)
    passed = result.returncode == (1 if args.expect_failure else 0)
    report = {"passed": passed, "expected_regression": args.expect_failure,
              "architecture": args.arch,
              "execution": "Rosetta" if args.arch == "x86_64" and platform.machine() == "arm64" else "native",
              "production_methods_sha256": hashlib.sha256("\n".join(methods).encode()).hexdigest(),
              "exit_code": result.returncode, "output": (result.stdout + result.stderr).strip(),
              "scope": "Actual production clock methods with isolated model/order/persistence stubs; no native pointer gesture claim"}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
