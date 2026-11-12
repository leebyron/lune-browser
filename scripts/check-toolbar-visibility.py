#!/usr/bin/env python3
"""Exercise the production toolbar mode, hover rail and engagement decisions."""
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
native = (frame / 'browser_frame_view_mac.mm').read_text()
menu = (frame / 'system_menu_model_delegate.cc').read_text()
def method(text, start, end):
    at = text.index(start)
    return text[at:text.index(end, at)]
getter = method(view, 'bool BrowserView::IsTopChromeHoverEnabled()',
                'bool BrowserView::IsPointInTopChromeHoverArea(')
rail = method(native, '  const bool in_rail =', '  const bool in_window =')
start = native.index('  const bool present =', native.index(
    'void BrowserFrameViewMac::UpdateFloatingAddressBar()'))
present = native[start:native.index(';', start) + 1]
selected = method(menu, '    const auto* prefs = browser_->GetProfile()->GetPrefs();',
                  '\n  }\n\n  if (command_id == IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN)')
execute = method(menu[menu.index('void SystemMenuModelDelegate::ExecuteCommand'):],
                 '    auto* prefs = browser_->GetProfile()->GetPrefs();',
                 '\n  }\n  switch (command_id)')
# The new preference gates entry, not page-column geometry/retention or sidebar entry.
assert 'if (!IsTopChromeHoverEnabled())' in view
assert 'IsTopChromeHoverEnabled' not in method(
    view, 'bool BrowserView::IsPointInTopChromeHoverArea(',
    'bool BrowserView::IsPointInZenTopTrigger(')
assert 'const bool in_sidebar_header = sidebar_header.Contains(cursor);' in native
assert 'in_hover_area && in_window &&' in native
prefix = r'''
#import <Foundation/Foundation.h>
#include <cassert>
#include <cstdio>
namespace prefs { enum { kHeliumZenModeTopChromePinned,
  kHeliumTopControlsOverlay, kHeliumTopControlsHoverDisabled }; }
enum { IDC_TOP_CONTROLS_HOVER=1, IDC_TOP_CONTROLS_ALWAYS,
       IDC_TOP_CONTROLS_OVERLAY, IDC_TOP_CONTROLS_NO_HOVER };
struct Prefs {
  bool values[3]={};
  bool GetBoolean(int p) const { return values[p]; }
  void SetBoolean(int p,bool v) { values[p]=v; }
  Prefs* GetPrefs() { return this; }
  Prefs* GetProfile() { return this; }
};
struct BrowserView {
  Prefs prefs; bool held=false, pinned=false;
  Prefs* GetProfile() const { return const_cast<Prefs*>(&prefs); }
  bool IsTopChromeHoverEnabled() const;
  bool IsTopChromeRevealHeldForMenu() const { return held; }
  bool IsZenModeTopChromePinned() const { return pinned; }
};
namespace helium {
  bool pointer_in_rail;
  bool IsPointerInNativeRevealRail(BrowserView*, bool) { return pointer_in_rail; }
}
@interface Header : NSObject
@property(nonatomic, getter=isPresented) BOOL presented;
@end
@implementation Header
@end
'''
source = prefix + getter + '\nbool Selected(Prefs* browser_,int command_id) {\n' + selected + '\n}\n'
source += 'void Execute(Prefs* browser_,int command_id) {\n' + execute + '\n}\n'
source += 'bool Rail(BrowserView* browser_view,bool in_hover_area) {\n' + rail + 'return in_rail;\n}\n'
source += '''bool Present(BrowserView* browser_view,Header* floating_address_bar_,
 bool customize_open,bool dragging,bool resizing,bool window_menu_open,
 bool in_rail,bool in_sidebar_header,bool within_retention,bool editing,bool bubble_open) {
''' + present + '\nreturn present;\n}\n'
source += r'''
int main() { @autoreleasepool {
  Prefs prefs;
  for (unsigned mask=0;mask<8;++mask) {
    for(int p=0;p<3;++p) prefs.values[p]=mask&(1<<p);
    int checked=0;
    for(int cmd=1;cmd<=4;++cmd) checked+=Selected(&prefs,cmd);
    assert(checked==1);
    for(int cmd=1;cmd<=4;++cmd) {
      for(int p=0;p<3;++p) prefs.values[p]=mask&(1<<p);
      Execute(&prefs,cmd);
      assert(Selected(&prefs,cmd));
      assert(prefs.values[0]==(cmd==2||cmd==3));
      assert(prefs.values[1]==(cmd==3));
      assert(prefs.values[2]==(cmd==4));
    }
  }
  BrowserView browser;
  Header* header=[[Header alloc] init];
  for (bool disabled:{false,true}) {
    browser.prefs.values[2]=disabled;
    for (bool area:{false,true}) for (bool pointer:{false,true}) {
      helium::pointer_in_rail=pointer;
      assert(Rail(&browser,area)==(!disabled&&area&&pointer));
    }
    // With page-edge reveal disabled, sidebar, editing, active bubbles and
    // explicit popup holds continue to reveal/retain the exact native header.
    for(unsigned mask=0;mask<1024;++mask) {
      auto bit=[&](unsigned n){return bool(mask&(1<<n));};
      browser.held=bit(0);browser.pinned=bit(1);header.presented=bit(2);
      const bool rail=Rail(&browser,true);
      const bool actual=Present(&browser,header,bit(3),bit(4),bit(5),bit(6),
                                rail,bit(7),false,bit(8),bit(9));
      const bool expected=bit(0)||bit(1)||bit(3)||
          ((bit(4)||bit(5)||bit(6))?bit(2):
           (rail||bit(7)||bit(8)||(bit(2)&&bit(9))));
      assert(actual==expected);
    }
  }
  puts("PASS toolbar mode exclusivity, preference writes, disabled rail and 2048 native engagement states");
} }
'''
source = source.replace('#include <cstdio>', '#include <cstdio>\n#include <initializer_list>')
with tempfile.TemporaryDirectory(prefix='lune-toolbar-visibility-') as temp:
    src, binary = Path(temp)/'fixture.mm', Path(temp)/'fixture'
    src.write_text(source)
    subprocess.run(['/usr/bin/xcrun', 'clang++', '-std=c++20', '-fobjc-arc',
                    '-arch', args.arch, '-framework', 'Foundation',
                    str(src), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
