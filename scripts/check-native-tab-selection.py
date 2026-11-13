#!/usr/bin/env python3
"""Check native selected-tab background roles using the production AppKit mixer."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', required=True, choices=('arm64', 'x86_64'))
args = parser.parse_args()
source = (args.source / 'chrome/browser/ui/color/mac/native_chrome_color_mixer_mac.mm').read_text()
source = source[source.index('namespace {'):]
ids = sorted(set(re.findall(r'(?:ui::)?\b(kColor\w+)', source)) | {
    'kColorTabBackgroundSelectedFrameActive', 'kColorTabBackgroundSelectedFrameInactive',
    'kColorTabBackgroundSelectedHoverFrameActive', 'kColorTabBackgroundSelectedHoverFrameInactive',
})
prefix = r'''
#import <AppKit/AppKit.h>
#include <cassert>
#include <cstdint>
#include <map>
using SkColor = uint32_t;
namespace skia {
SkColor NSDeviceColorToSkColor(NSColor* color) {
  return (uint32_t(lround(color.alphaComponent * 255)) << 24) |
         (uint32_t(lround(color.redComponent * 255)) << 16) |
         (uint32_t(lround(color.greenComponent * 255)) << 8) |
         uint32_t(lround(color.blueComponent * 255));
}
}
namespace ui {
enum ColorId { IDS };
struct ColorProviderKey {
 enum class FrameStyle { kSystem, kDefault }; FrameStyle frame_style=FrameStyle::kSystem;
 enum class ForcedColors { kNone, kActive }; ForcedColors forced_colors=ForcedColors::kNone;
 enum class ColorMode { kLight, kDark }; ColorMode color_mode=ColorMode::kLight;
 enum class ContrastMode { kNormal, kHigh }; ContrastMode contrast_mode=ContrastMode::kNormal;
 bool custom_theme=false,app_controller=false;
};
struct Recipe {
 SkColor color=0; int alias=-1;
 Recipe()=default; Recipe(SkColor c):color(c){} Recipe(ColorId id):alias(id){}
};
struct ColorMixer {
 std::map<int,Recipe> recipes;
 Recipe& operator[](ColorId id){return recipes[id];}
};
struct ColorProvider {
 ColorMixer mixer; int mixers=0;
 ColorMixer& AddMixer(){++mixers;return mixer;}
 SkColor GetColor(ColorId id) const {
  const auto& r=mixer.recipes.at(id);
  return r.alias<0?r.color:GetColor(static_cast<ColorId>(r.alias));
 }
};
}
using namespace ui;
'''.replace('IDS', ','.join(ids))
test = r'''
int main(){@autoreleasepool {
 [NSApplication sharedApplication];
 for(bool dark:{false,true})for(bool high:{false,true}) {
  ui::ColorProviderKey key;
  key.color_mode=dark?ui::ColorProviderKey::ColorMode::kDark:ui::ColorProviderKey::ColorMode::kLight;
  key.contrast_mode=high?ui::ColorProviderKey::ContrastMode::kHigh:ui::ColorProviderKey::ContrastMode::kNormal;
  ui::ColorProvider provider;
  // Distinct inherited roles reproduce the old mismatch rather than hiding it.
  for(auto id:{kColorTabBackgroundSelectedFrameActive,kColorTabBackgroundSelectedFrameInactive,
               kColorTabBackgroundSelectedHoverFrameActive,kColorTabBackgroundSelectedHoverFrameInactive})
   provider.mixer[id]={SkColor(0xfffefdfc)};
  AddNativeChromeColorMixer(&provider,key);
  assert(provider.mixers==1);
  for(auto pair:{std::pair{kColorTabBackgroundSelectedFrameActive,kColorTabBackgroundActiveFrameActive},
                 std::pair{kColorTabBackgroundSelectedFrameInactive,kColorTabBackgroundActiveFrameInactive},
                 std::pair{kColorTabBackgroundSelectedHoverFrameActive,kColorTabBackgroundActiveFrameActive},
                 std::pair{kColorTabBackgroundSelectedHoverFrameInactive,kColorTabBackgroundActiveFrameInactive}})
   assert(provider.GetColor(pair.first)==provider.GetColor(pair.second));
  for(int exclusion:{0,1,2,3}) {
   auto excluded=key;
   if(exclusion==0)excluded.frame_style=ui::ColorProviderKey::FrameStyle::kDefault;
   if(exclusion==1)excluded.custom_theme=true;
   if(exclusion==2)excluded.app_controller=true;
   if(exclusion==3)excluded.forced_colors=ui::ColorProviderKey::ForcedColors::kActive;
   ui::ColorProvider untouched;AddNativeChromeColorMixer(&untouched,excluded);
   assert(untouched.mixers==0 && untouched.mixer.recipes.empty());
  }
 }
 puts("PASS: native selected and active backgrounds match in light/dark, normal/high contrast, hover and window activation; theme/app/forced-color exclusions preserved");
}}
'''
with tempfile.TemporaryDirectory(prefix='lune-native-tab-selection-') as tmp:
    fixture = Path(tmp) / 'selection.mm'
    fixture.write_text(prefix + source + test)
    exe = Path(tmp) / 'selection'
    subprocess.run(['xcrun', 'clang++', '-std=c++20', '-fobjc-arc', '-arch', args.arch,
                    '-framework', 'AppKit', str(fixture), '-o', str(exe)], check=True)
    subprocess.run(['/usr/bin/arch', '-' + args.arch, str(exe)], check=True)
