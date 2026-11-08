#!/usr/bin/env python3
"""Exercise production media-controller policy and floating order in isolation.

The item manager, view tree, and preference are stand-ins. Browser playback,
bubble anchoring, and native geometry still require live integration checks.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=('arm64', 'x86_64'), required=True)
args = parser.parse_args()
controller = args.source / 'chrome/browser/ui/global_media_controls'


def without_includes(text):
    return re.sub(r'^#include .*\n', '', text, flags=re.M)


header = without_includes((controller / 'media_toolbar_button_controller.h').read_text())
impl = without_includes((controller / 'media_toolbar_button_controller.cc').read_text())
toolbar = (args.source / 'chrome/browser/ui/views/toolbar/toolbar_view.cc').read_text()
start = toolbar.index('void ToolbarView::OnShowMediaButtonChanged()')
policy = toolbar[start:toolbar.index('\nvoid ', start + 1)]
start = toolbar.index('  if (home_ && home_->parent() == host)')
order = toolbar[start:toolbar.index('  AbortToolbarContainerAnimationsForZenReveal();', start)]

prefix = r'''
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <vector>
#define CHECK(value, ...) assert(value)
template<class T> using raw_ptr = T*;
namespace global_media_controls {
struct MediaItemManagerObserver {
  virtual ~MediaItemManagerObserver() = default;
  virtual void OnItemListChanged() = 0;
  virtual void OnMediaDialogOpened() = 0;
  virtual void OnMediaDialogClosed() = 0;
};
struct MediaItemManager {
  bool active = false, frozen = false, dialog = false;
  MediaItemManagerObserver* observer = nullptr;
  void AddObserver(MediaItemManagerObserver* o) { assert(!observer); observer = o; }
  void RemoveObserver(MediaItemManagerObserver* o) { assert(observer == o); observer = nullptr; }
  bool HasActiveItems() const { return active; }
  bool HasFrozenItems() const { return frozen; }
  bool HasOpenDialog() const { return dialog; }
};
}
struct MediaToolbarButtonControllerDelegate {
  bool visible = false, enabled = false;
  int shows = 0, hides = 0;
  void Show() { visible = true; ++shows; }
  void Hide() { visible = false; ++hides; }
  void Enable() { enabled = true; }
  void Disable() { enabled = false; }
  void MaybeShowStopCastingPromo() {}
  void MaybeShowLocalMediaCastingPromo() {}
};
'''
fixture = r'''
struct MediaButton {
  MediaToolbarButtonController* controller;
  MediaToolbarButtonController* GetController() { return controller; }
};
struct View {
  View* owner = nullptr;
  std::vector<View*> children;
  View* parent() { return owner; }
  void ReorderChildView(View* child, int index) {
    auto found = std::find(children.begin(), children.end(), child);
    assert(found != children.end());
    children.erase(found);
    children.insert(children.begin() + index, child);
  }
};
struct ToolbarView {
  MediaButton* media_button_ = nullptr;
  struct Pref { bool value = true; bool GetValue() const { return value; } } show_media_button_;
  View* sidebar_controls_host_ = nullptr;
  std::vector<int> floating_controls_state_;
  View* home_ = nullptr;
  View* media_button_view_ = nullptr;
  void InvalidateLayout() {}
  void OnShowMediaButtonChanged();
  void Arrange(View* host);
};
'''
tests = r'''
int main() {
  global_media_controls::MediaItemManager manager;
  MediaToolbarButtonControllerDelegate delegate;
  {
    MediaToolbarButtonController controller(&delegate, &manager);
    MediaButton button{&controller};
    ToolbarView toolbar;
    toolbar.OnShowMediaButtonChanged();  // A toolbar with no media backend.
    toolbar.media_button_ = &button;
    View sidebar;
    assert(!delegate.visible);
    manager.active = true;
    manager.observer->OnItemListChanged();
    assert(delegate.visible && delegate.enabled);
    toolbar.sidebar_controls_host_ = &sidebar;
    toolbar.OnShowMediaButtonChanged();
    assert(!delegate.visible);  // Before floating host attachment.
    toolbar.floating_controls_state_.push_back(1);
    toolbar.OnShowMediaButtonChanged();
    assert(delegate.visible && delegate.enabled);
    int shows = delegate.shows;
    toolbar.OnShowMediaButtonChanged();
    assert(delegate.shows == shows);  // Repeated layout must not retrigger Show.
    toolbar.show_media_button_.value = false;
    toolbar.OnShowMediaButtonChanged();
    assert(!delegate.visible);
    manager.observer->OnItemListChanged();
    assert(!delegate.visible);  // Playback cannot override the preference.
    toolbar.show_media_button_.value = true;
    toolbar.OnShowMediaButtonChanged();
    assert(delegate.visible && delegate.enabled);
    manager.active = false;
    manager.frozen = true;
    manager.observer->OnItemListChanged();
    assert(delegate.visible && !delegate.enabled);
    manager.dialog = true;
    manager.observer->OnMediaDialogOpened();
    assert(delegate.visible && delegate.enabled);
    manager.frozen = false;
    manager.observer->OnItemListChanged();
    assert(delegate.visible);  // Open dialog keeps the last item available.
    manager.dialog = false;
    manager.observer->OnMediaDialogClosed();
    assert(!delegate.visible);
    manager.active = true;
    manager.observer->OnItemListChanged();
    assert(delegate.visible && delegate.enabled);
    toolbar.floating_controls_state_.clear();
    toolbar.OnShowMediaButtonChanged();
    assert(!delegate.visible);
    toolbar.sidebar_controls_host_ = nullptr;
    toolbar.OnShowMediaButtonChanged();
    assert(delegate.visible && delegate.enabled);  // Classic toolbar restored.
    puts("PASS: preference, host attachment/restoration, active/frozen/dialog lifecycle");

    View host, home, media, extensions, more;
    for (auto* view : {&home, &media, &extensions, &more}) view->owner = &host;
    toolbar.home_ = &home;
    for (bool webui : {false, true}) {
      View webui_owner;
      webui_owner.owner = &host;
      View* media_owner = webui ? &webui_owner : &media;
      toolbar.media_button_view_ = media_owner;
      host.children = {&extensions, &home, &more, media_owner};
      toolbar.Arrange(&host);
      assert((host.children == std::vector<View*>{media_owner, &home, &extensions, &more}));
      toolbar.Arrange(&host);
      assert(host.children[0] == media_owner && host.children[1] == &home);
    }
    toolbar.media_button_view_ = nullptr;
    host.children = {&extensions, &more, &home};
    toolbar.Arrange(&host);
    assert((host.children == std::vector<View*>{&home, &extensions, &more}));
    puts("PASS: media owner precedes Home; other order preserved; no abstract-button cast");
  }
  assert(!manager.observer);
  puts("PASS: controller removes its item-manager observation on destruction");
}
'''
with tempfile.TemporaryDirectory(prefix='lune-media-toolbar-') as temp:
    source = Path(temp) / 'test.cc'
    binary = Path(temp) / 'test'
    source.write_text(prefix + header + impl + fixture + policy +
                      '\nvoid ToolbarView::Arrange(View* host) {\n' + order + '}\n' + tests)
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-arch', args.arch,
                    str(source), '-o', str(binary)], check=True)
    subprocess.run(['/usr/bin/arch', '-' + args.arch, str(binary)], check=True)
