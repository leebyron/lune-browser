from pathlib import Path
import argparse, subprocess, tempfile
parser = argparse.ArgumentParser(description='Check production detached-sidebar color policy with native AppKit appearances.')
parser.add_argument('source', type=Path)
parser.add_argument('--arch', required=True, choices=('arm64', 'x86_64'))
args = parser.parse_args()
tmp = tempfile.TemporaryDirectory(prefix='lune-sidebar-colors-')
o=Path(tmp.name);s=args.source
t=(s/'chrome/browser/ui/views/helium/native_frame_materials_mac.mm').read_text();fn=t[t.index('std::optional<SkColor> NativeGlassColor('):t.index('bool IsNativeWindowLiveResizing(')]
h=(s/'chrome/browser/ui/views/helium/native_frame_materials.h').read_text();enum=h[h.index('enum class NativeGlassColorRole'):h.index('std::optional<SkColor> NativeGlassColor')]
prefix=r'''
#import <AppKit/AppKit.h>
#import <objc/runtime.h>
#include <optional>
#include <string>
#include <cassert>
#include <cmath>
using SkColor = uint32_t;
constexpr SkColor SK_ColorBLACK=0xff000000;
SkColor SkColorSetARGB(unsigned a,unsigned r,unsigned g,unsigned b){return (a<<24)|(r<<16)|(g<<8)|b;}
constexpr int kColorTabBackgroundActiveFrameActive=1,kColorTabBackgroundActiveFrameInactive=2,
 kColorTabForegroundActiveFrameActive=3,kColorTabForegroundActiveFrameInactive=4,
 kColorTabBackgroundInactiveHoverFrameActive=5,kColorTabBackgroundInactiveHoverFrameInactive=6;
namespace ui {
struct ColorProviderKey {
 enum class ColorMode { kLight,kDark }; ColorMode color_mode=ColorMode::kLight;
 enum class ContrastMode { kNormal,kHigh }; ContrastMode contrast_mode=ContrastMode::kNormal;
 enum class ForcedColors { kNone,kActive }; ForcedColors forced_colors=ForcedColors::kNone;
 int theme=0;
};
struct Provider { ColorProviderKey key; SkColor GetColor(int role)const {
 return 0xff000000 | key.theme<<16 | (key.color_mode==ColorProviderKey::ColorMode::kDark ? 0x100:0) | role;
}};
struct ColorProviderManager { Provider provider; static auto& Get(){static ColorProviderManager m;return m;}
 Provider* GetColorProviderFor(ColorProviderKey key){provider.key=key;return &provider;}
};
struct NativeTheme {
 enum class PreferredColorScheme { kLight,kDark };
 static NativeTheme* GetInstanceForNativeUi(){static NativeTheme n;return &n;}
 PreferredColorScheme preferred_color_scheme(){return PreferredColorScheme::kLight;}
};
}
struct ThemeService {
 enum class BrowserColorScheme { kLight,kDark,kSystem }; bool device=false;
 BrowserColorScheme GetBrowserColorScheme(){return BrowserColorScheme::kLight;}
 bool UsingDeviceTheme(){return device;}
};
struct ThemeServiceFactory { static ThemeService* GetForProfile(ThemeService* p){return p;} };
struct BrowserView;
namespace views {
struct Native { NSView* view; NSView* GetNativeNSView(){return view;} };
struct Widget {
 NSView* native=[[NSView alloc]init];std::string name="Floating sidebar controls";
 BrowserView* owner=nullptr;ui::ColorProviderKey key;bool active=true;
 Native GetNativeView(){return {native};} BrowserView* GetNativeWindow(){return owner;}
 const std::string& GetName(){return name;}
 ui::ColorProviderKey GetColorProviderKey(){return key;}
 bool ShouldPaintAsActive(){return active;}
};
struct View { Widget* widget;Widget* GetWidget()const{return widget;} };
}
struct BrowserView {
 views::Widget widget;ThemeService theme;bool attached=true;
 static BrowserView* GetBrowserViewForNativeWindow(BrowserView* p){return p;}
 views::Widget* browser_widget(){return &widget;} views::Widget* GetWidget(){return &widget;}
 ThemeService* GetProfile(){return &theme;}
 void* GetColorProvider(){return attached?this:nullptr;}
};
char kGlassControlAppearanceKey;
bool IsNativeGlassControl(const views::View* v){return v && v->GetWidget();}
'''
test=r'''
int main(){@autoreleasepool {
 [NSApplication sharedApplication];
 BrowserView browser;views::Widget child;child.owner=&browser;views::View row{&child};
 NSAppearance* light=[NSAppearance appearanceNamed:NSAppearanceNameAqua];
 NSAppearance* dark=[NSAppearance appearanceNamed:NSAppearanceNameDarkAqua];
 auto appearance=[&](NSAppearance* a){objc_setAssociatedObject(child.native,&kGlassControlAppearanceKey,a,OBJC_ASSOCIATION_RETAIN_NONATOMIC);};
 auto color=[&](NativeGlassColorRole role){return *NativeGlassColor(&row,role);};
 for(int theme : {2,7})for(bool is_dark : {false,true})for(bool active : {false,true}) {
  browser.widget.key.theme=theme;browser.widget.active=active;appearance(is_dark?dark:light);
  const uint32_t base=0xff000000 | theme<<16 | (is_dark?0x100:0);
  assert(color(NativeGlassColorRole::kSelection)==(base|(active?1:2)));
  assert(color(NativeGlassColorRole::kSelectedLabel)==(base|(active?3:4)));
  assert(color(NativeGlassColorRole::kHover)==(base|(active?5:6)));
 }
 appearance(light);browser.widget.key.theme=7;browser.widget.active=true;
 const auto themed=color(NativeGlassColorRole::kSelection);
 browser.theme.device=true;const auto system=color(NativeGlassColorRole::kSelection);assert(system!=themed);
 browser.theme.device=false;child.name="Floating browser actions";assert(color(NativeGlassColorRole::kSelection)==system);
 child.name="Floating sidebar controls";browser.widget.key.contrast_mode=ui::ColorProviderKey::ContrastMode::kHigh;
 assert(color(NativeGlassColorRole::kSelection)==system);
 browser.widget.key.contrast_mode=ui::ColorProviderKey::ContrastMode::kNormal;
 browser.widget.key.forced_colors=ui::ColorProviderKey::ForcedColors::kActive;
 assert(color(NativeGlassColorRole::kSelection)==system);
 browser.widget.key.forced_colors=ui::ColorProviderKey::ForcedColors::kNone;
 browser.attached=false;assert(color(NativeGlassColorRole::kSelection)==system);
 browser.attached=true;const auto label=color(NativeGlassColorRole::kLabel);
 browser.theme.device=true;assert(color(NativeGlassColorRole::kLabel)==label);
 assert(!NativeGlassColor(nullptr,NativeGlassColorRole::kLabel));
 puts("PASS: owning theme, actual glass scheme, active/inactive roles, System, header isolation, accessibility fallback, startup and native labels");
}}
'''
p=o/'sidebar-colors.mm';p.write_text(prefix+enum+fn+test);arch=args.arch
exe=o/f'sidebar-colors-{arch}'
subprocess.run(['xcrun','clang++','-std=c++20','-fobjc-arc','-arch',arch,'-framework','AppKit',str(p),'-o',str(exe)],check=True)
subprocess.run(['/usr/bin/arch','-'+arch,str(exe)],check=True)
