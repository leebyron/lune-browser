#!/usr/bin/env python3
"""Exercise the production command registry/dispatch with window and policy doubles.

This verifies palette decisions, not Chromium's independently owned handlers.
Native focus, real policy enforcement and window lifetime need browser checks.
"""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
args = parser.parse_args()
ui = args.source / 'chrome/browser/ui/helium'
registry = (ui / 'helium_command_bar_commands.cc').read_text()
model = (ui / 'helium_command_bar_model.cc').read_text()

def function(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

labels = {m.attrib['name']: ''.join(m.itertext()).strip()
          for m in ET.parse(args.source / 'chrome/app/generated_resources.grd').iter('message')
          if m.attrib.get('name', '').startswith('IDS_COMMAND_BAR_')}
for message in ET.parse(args.source / 'chrome/app/chromium_strings.grd').iter('message'):
    if message.attrib.get('name') == 'IDS_SIDE_PANEL_CUSTOMIZE_CHROME_TITLE':
        labels[message.attrib['name']] = ''.join(message.itertext()).strip()
commands = sorted(set(re.findall(r'\bIDC_[A-Z_]+', registry)))
label_ids = sorted(labels)
definitions = '\n'.join(f'constexpr int {name} = {n};'
                        for n, name in enumerate(commands + label_ids, 1))
label_switch = '\n'.join(f'case {name}: return u"{labels[name]}";' for name in label_ids)
body = '\n'.join(line for line in registry.splitlines() if not line.startswith('#include'))
controller = (ui / 'helium_command_bar_controller.cc').read_text()
mode_helpers = r'''
namespace ui {
constexpr int VKEY_OEM_2=1,VKEY_P=2,VKEY_T=3;
constexpr int EF_PLATFORM_ACCELERATOR=1,EF_SHIFT_DOWN=2;
struct Accelerator {
  int key,flags;
  int key_code() const{return key;}
  int modifiers() const{return flags;}
};
}
struct CommandMode {
  std::string scope_keyword_;
  std::u16string last_query_;
  bool commands_only_=false,hidden=false;
  struct Input {std::u16string text;void SetInputText(const std::u16string& q){text=q;}} input;
  Input* view_=&input;
  bool InCommandMode() const;
  void OnEscapePressed();
  void ExitScope(){scope_keyword_.clear();}
  void OnQueryChanged(const std::u16string& query){last_query_=query;}
  void HideSoon(){hidden=true;}
};
''' + function(controller, 'bool IsCommandSearchAccelerator(') + '\n' + function(
    controller, 'bool HeliumCommandBarController::InCommandMode()').replace(
        'HeliumCommandBarController::', 'CommandMode::') + '\n' + function(
    controller, 'void HeliumCommandBarController::OnEscapePressed()').replace(
        'HeliumCommandBarController::', 'CommandMode::')

program = r'''
#include <algorithm>
#include <cassert>
#include <iostream>
#include <iterator>
#include <map>
#include <optional>
#include <set>
#include <string>
#include <vector>
''' + definitions + r'''
namespace base {
struct Time {
  double seconds=2000000000;
  static Time Now(){return {};}
  double InSecondsFSinceUnixEpoch() const{return seconds;}
};
struct DictValue {
  std::map<std::string,DictValue> dicts;
  std::map<std::string,int> ints;
  std::map<std::string,double> doubles;
  const DictValue* FindDict(const char* key) const {
    auto it=dicts.find(key);return it==dicts.end()?nullptr:&it->second;
  }
  DictValue* EnsureDict(const char* key){return &dicts[key];}
  std::optional<int> FindInt(const char* key) const {
    auto it=ints.find(key);return it==ints.end()?std::nullopt:std::optional(it->second);
  }
  std::optional<double> FindDouble(const char* key) const {
    auto it=doubles.find(key);return it==doubles.end()?std::nullopt:std::optional(it->second);
  }
  void Set(const char* key,int value){ints[key]=value;}
  void Set(const char* key,double value){doubles[key]=value;}
};
enum TrimPositions { TRIM_ALL, TRIM_LEADING };
void TrimWhitespace(const std::u16string& input, TrimPositions mode, std::u16string* out) {
  const auto start = input.find_first_not_of(u" \t\r\n");
  *out = start == input.npos ? u"" : input.substr(start,
      (mode == TRIM_ALL ? input.find_last_not_of(u" \t\r\n") + 1 : input.size()) - start);
}
namespace i18n {
std::u16string ToLower(std::u16string text) {
  for (auto& c : text) if (c >= u'A' && c <= u'Z') c += 32;
  return text;
}
}
std::u16string UTF8ToUTF16(const std::string& text) {return {text.begin(),text.end()};}
enum { TRIM_WHITESPACE, SPLIT_WANT_NONEMPTY };
std::vector<std::string> SplitString(std::string s, const char*, int, int) {
  std::vector<std::string> v;
  for (size_t begin=0,end;begin<s.size();begin=end+1) {
    end=s.find('|',begin);if(end==s.npos)end=s.size();v.push_back(s.substr(begin,end-begin));
  }
  return v;
}
}
namespace l10n_util {
std::u16string GetStringUTF16(int id) {switch(id) {
''' + label_switch + r'''
default: assert(false); return {};}}
}
namespace prefs { constexpr char kHeliumVerticalRightAligned[]="right"; constexpr char kHeliumCommandBarCommandUsage[]="usage"; constexpr char kVerticalCollapseShortcut[]="collapse"; constexpr char kCopyPageUrlShortcut[]="copy"; }
struct PrefService {
  bool right=false,collapse=false,copy=false;
  bool GetBoolean(const char* key){
    if(std::string(key)=="collapse")return collapse;
    if(std::string(key)=="copy")return copy;
    return right;
  }
  base::DictValue usage;
  const base::DictValue& GetDict(const char*){return usage;}
};
struct ScopedDictPrefUpdate {
  PrefService* prefs;ScopedDictPrefUpdate(PrefService* p,const char*):prefs(p){}
  base::DictValue* operator->(){return &prefs->usage;}
};
struct Profile {
  PrefService prefs;bool off_the_record=false;Profile* original=nullptr;
  PrefService* GetPrefs(){return &prefs;}
  bool IsOffTheRecord(){return off_the_record;}
  Profile* GetOriginalProfile(){return original?original:this;}
};
namespace content {struct WebContents {};}
struct TabStripModel {
  enum {CommandTogglePinned,CommandToggleSiteMuted};
  bool active_present=true,pin_enabled=true,mute_enabled=true;
  bool pinned[2]={false,true},muted[2]={false,false};
  content::WebContents page;
  int active_index(){return 0;}
  content::WebContents* GetActiveWebContents(){return active_present?&page:nullptr;}
  bool IsContextMenuCommandEnabled(int i,int command){assert(i==0);return command==CommandTogglePinned?pin_enabled:mute_enabled;}
  bool IsTabPinned(int i){return pinned[i];}
  void SetTabPinned(int i,bool pin){pinned[i]=pin;}
  void SetSitesMuted(std::vector<int> indices,bool mute){for(int i:indices)muted[i]=mute;}
};
bool IsSiteMuted(const TabStripModel& strip,int i){return strip.muted[i];}
struct Window {bool fullscreen=false;bool IsFullscreen(){return fullscreen;}};
struct BrowserWindowInterface {
  enum class Type {TYPE_NORMAL,TYPE_APP};
  Type type=Type::TYPE_NORMAL;Profile profile;TabStripModel strip;Window window;
  std::set<int> unsupported,disabled;int executed=0;
  Type GetType(){return type;}Profile* GetProfile(){return &profile;}
  TabStripModel* GetTabStripModel(){return &strip;}Window* GetWindow(){return &window;}
};
struct HeliumLayoutStateController {
  static HeliumLayoutStateController* state;
  static HeliumLayoutStateController* From(BrowserWindowInterface*){return state;}
  int layout=0;bool zen=true;
  bool IsClassicLayout(){return layout==0;}bool IsCompactLayout(){return layout==1;}
  bool IsVerticalLayout(){return layout==2;}bool IsDynamicLayout(){return layout==3;}
  bool IsZenModeEnabled(){return zen;}
};
HeliumLayoutStateController* HeliumLayoutStateController::state=nullptr;
struct BrowserView {
  static BrowserView* state;
  static BrowserView* GetBrowserViewForBrowser(BrowserWindowInterface*){return state;}
  bool side=false,top=false;
  bool IsZenModeSideChromePinned(){return side;}bool IsZenModeTopChromePinned(){return top;}
  void ToggleZenModeSideChrome(){side=!side;}
};
BrowserView* BrowserView::state=nullptr;
namespace tabs {
struct VerticalTabStripStateController {
  static VerticalTabStripStateController* state;
  static VerticalTabStripStateController* From(BrowserWindowInterface*){return state;}
  bool collapsed=false,display=true;
  bool IsCollapsed(){return collapsed;}bool ShouldDisplayVerticalTabs(){return display;}
  void RequestCollapse(bool c){collapsed=c;}
};
VerticalTabStripStateController* VerticalTabStripStateController::state=nullptr;
}
namespace chrome {
bool SupportsCommand(BrowserWindowInterface* b,int id){return !b->unsupported.contains(id);}
bool IsCommandEnabled(BrowserWindowInterface* b,int id){return !b->disabled.contains(id);}
bool ExecuteCommand(BrowserWindowInterface* b,int id){b->executed=id;return true;}
}
namespace browser_shortcuts {
struct ShortcutInfo {std::u16string display_text;};
struct CommandInfo {int command_id;std::vector<ShortcutInfo> accelerators;};
struct BrowserShortcutService {
  std::vector<CommandInfo> commands;
  const std::vector<CommandInfo>& GetCommands(){return commands;}
};
struct BrowserShortcutServiceFactory {
  static BrowserShortcutService* service;
  static BrowserShortcutService* GetForProfile(Profile*){return service;}
};
BrowserShortcutService* BrowserShortcutServiceFactory::service=nullptr;
}
struct HeliumCommandBarItem {
  enum class Type {kCommand};Type type;int command=0,score=0;
  std::u16string title,shortcut;std::string symbol_name;
};
namespace helium_command_bar_model {
constexpr int kPinSidebar=-1;
constexpr int kScoreExact=140,kScorePrefix=70,kScoreWord=45,kScoreSubstring=20;
''' + function(model, 'bool IsWordBoundary(') + '\n' + function(model, 'int ScoreText(') + '\n}\n' + body + mode_helpers + r'''
int main() {
  using namespace helium_command_bar_model;
  assert(IsCommandSearchAccelerator({ui::VKEY_OEM_2,ui::EF_PLATFORM_ACCELERATOR}));
  assert(IsCommandSearchAccelerator({ui::VKEY_P,ui::EF_PLATFORM_ACCELERATOR|ui::EF_SHIFT_DOWN}));
  assert(!IsCommandSearchAccelerator({ui::VKEY_P,ui::EF_PLATFORM_ACCELERATOR}));
  assert(!IsCommandSearchAccelerator({ui::VKEY_OEM_2,ui::EF_PLATFORM_ACCELERATOR|ui::EF_SHIFT_DOWN}));
  assert(!IsCommandSearchAccelerator({ui::VKEY_T,ui::EF_PLATFORM_ACCELERATOR}));
  CommandMode mode;
  mode.commands_only_=true;assert(mode.InCommandMode());
  mode.OnEscapePressed();assert(mode.hidden);
  mode.hidden=false;mode.commands_only_=true;mode.last_query_=u"find";
  mode.OnEscapePressed();assert(mode.hidden&&mode.last_query_==u"find");
  mode.commands_only_=false;mode.hidden=false;
  mode.last_query_=u"/find";assert(mode.InCommandMode());
  mode.OnEscapePressed();assert(!mode.InCommandMode()&&mode.last_query_==u"find");
  mode.last_query_=u"//example.com";assert(!mode.InCommandMode());
  mode.commands_only_=true;mode.scope_keyword_="!g";
  assert(!mode.InCommandMode());  // Engine scopes own their query.
  BrowserWindowInterface browser;
  HeliumLayoutStateController layout;HeliumLayoutStateController::state=&layout;
  BrowserView view;BrowserView::state=&view;
  tabs::VerticalTabStripStateController vertical;
  tabs::VerticalTabStripStateController::state=&vertical;
  auto find=[&](const std::u16string& q,bool scope=true){return CommandsForQuery(&browser,q,scope);};
  auto get=[&](int command){auto item=CommandForId(&browser,command);assert(item);return *item;};
  auto has=[&](const auto& rows,int command){return std::ranges::any_of(rows,[&](const auto& r){return r.command==command;});};
  assert(IsCommandQuery(u"/reload") && IsCommandQuery(u"  / reload"));
  assert(!IsCommandQuery(u"//") && !IsCommandQuery(u"//example.com"));
  assert(!IsCommandQuery(u">reload"));
  assert(!IsCommandQuery(u"!g / reload") && !IsCommandQuery(u"normal / text"));
  assert(find(u"",false).empty());
  auto all=find(u"/");assert(all.size()>9);
  std::set<int> ids;
  for(const auto& item:all){assert(!item.title.empty()&&!item.symbol_name.empty());assert(ids.insert(item.command).second);}
  assert(find(u"/undo close tab")[0].command==IDC_RESTORE_TAB);
  assert(find(u"/ReOpEn")[0].command==IDC_RESTORE_TAB);
  assert(find(u"/hard refresh")[0].command==IDC_RELOAD_BYPASSING_CACHE);
  assert(find(u"/private browsing")[0].command==IDC_NEW_INCOGNITO_WINDOW);
  assert(find(u"/console")[0].command==IDC_DEV_TOOLS_CONSOLE);
  assert(find(u"/customize")[0].command==IDC_SHOW_CUSTOMIZE_CHROME_SIDE_PANEL);
  assert(find(u"/save as pdf")[0].command==IDC_PRINT);
  assert(find(u"/no match xyz").empty());
  browser.disabled.insert(IDC_RESTORE_TAB);assert(find(u"/undo close tab").empty());
  browser.unsupported.insert(IDC_DEV_TOOLS_CONSOLE);assert(find(u"/console").empty());
  auto print=get(IDC_PRINT);browser.disabled.insert(IDC_PRINT);
  assert(!ExecutePaletteCommand(&browser,print)&&browser.executed==0);
  browser.disabled.clear();assert(ExecutePaletteCommand(&browser,print)&&browser.executed==IDC_PRINT);
  auto pin=get(IDC_WINDOW_PIN_TAB);assert(pin.title==u"Pin Tab");
  assert(ExecutePaletteCommand(&browser,pin));
  assert(browser.strip.pinned[0]&&browser.strip.pinned[1]);
  auto unpin=get(IDC_WINDOW_PIN_TAB);assert(unpin.title==u"Unpin Tab"&&unpin.symbol_name=="pin.slash");
  assert(!ExecutePaletteCommand(&browser,pin));
  assert(ExecutePaletteCommand(&browser,unpin));
  assert(!browser.strip.pinned[0]&&browser.strip.pinned[1]);
  browser.strip.pin_enabled=false;assert(!CommandForId(&browser,IDC_WINDOW_PIN_TAB));
  auto mute=get(IDC_WINDOW_MUTE_SITE);assert(ExecutePaletteCommand(&browser,mute));
  assert(browser.strip.muted[0]&&!browser.strip.muted[1]);
  assert(get(IDC_WINDOW_MUTE_SITE).title==u"Unmute Site");
  assert(!ExecutePaletteCommand(&browser,mute));
  assert(get(IDC_FULLSCREEN).title==u"Enter Fullscreen");browser.window.fullscreen=true;
  assert(get(IDC_FULLSCREEN).title==u"Exit Fullscreen");
  assert(!CommandForId(&browser,IDC_BROWSER_LAYOUT_VERTICAL_RIGHT));
  layout.layout=2;
  assert(get(IDC_BROWSER_LAYOUT_VERTICAL_RIGHT).title==u"Move Sidebar to Right");
  browser.profile.prefs.right=true;
  assert(get(IDC_BROWSER_LAYOUT_VERTICAL_RIGHT).title==u"Move Sidebar to Left");
  assert(get(IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN).title==u"Pin Toolbar");view.top=true;
  assert(get(IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN).title==u"Unpin Toolbar");
  assert(ExecutePaletteCommand(&browser,get(kPinSidebar))&&view.side);
  assert(get(kPinSidebar).title==u"Unpin Sidebar");
  layout.zen=false;assert(!CommandForId(&browser,kPinSidebar));
  assert(!CommandForId(&browser,IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN));
  browser.strip.pin_enabled=true;
  auto& usage=browser.profile.prefs.usage;
  usage.dicts.clear();
  assert(find(u"/")[0].command==IDC_NEW_TAB);
  assert(ExecutePaletteCommand(&browser,get(IDC_PRINT)));
  assert(find(u"/")[0].command==IDC_PRINT);
  assert(ExecutePaletteCommand(&browser,get(IDC_ZOOM_PLUS)));
  assert(ExecutePaletteCommand(&browser,get(IDC_ZOOM_PLUS)));
  assert(find(u"/")[0].command==IDC_ZOOM_PLUS);
  assert(usage.FindDict("IDC_ZOOM_PLUS")->FindInt("count")==2);
  auto* record=usage.EnsureDict("IDC_RELOAD_BYPASSING_CACHE");
  record->Set("count",9999);record->Set("last_used",base::Time::Now().seconds);
  assert(find(u"/reload")[0].command==IDC_RELOAD);  // Match quality wins.
  assert(ExecutePaletteCommand(&browser,get(IDC_RELOAD_BYPASSING_CACHE)));
  assert(record->FindInt("count")==1000);  // Saturated count.
  usage.dicts.clear();
  RecordCommandUse(&browser.profile,IDC_PRINT);
  record=usage.EnsureDict("IDC_PRINT");record->Set("last_used",base::Time::Now().seconds-86400*31);
  RecordCommandUse(&browser.profile,IDC_ZOOM_PLUS);
  assert(find(u"/")[0].command==IDC_ZOOM_PLUS);  // Recency matters.
  auto count=usage.FindDict("IDC_ZOOM_PLUS")->FindInt("count");
  browser.profile.off_the_record=true;
  assert(ExecutePaletteCommand(&browser,get(IDC_ZOOM_PLUS)));
  assert(usage.FindDict("IDC_ZOOM_PLUS")->FindInt("count")==count);
  browser.profile.off_the_record=false;
  RecordCommandUse(&browser.profile,1234567);
  assert(usage.dicts.size()==2);  // Arbitrary IDs cannot create records.
  BrowserWindowInterface private_browser;
  private_browser.profile.off_the_record=true;
  private_browser.profile.original=&browser.profile;
  assert(CommandsForQuery(&private_browser,u"/",true)[0].command==IDC_ZOOM_PLUS);
  assert(ExecutePaletteCommand(&private_browser,*CommandForId(&private_browser,IDC_ZOOM_PLUS)));
  assert(private_browser.profile.prefs.usage.dicts.empty());
  assert(usage.FindDict("IDC_ZOOM_PLUS")->FindInt("count")==count);
  assert(CommandsForQuery(nullptr,u"/",true).empty());
  browser_shortcuts::BrowserShortcutService shortcuts;
  browser_shortcuts::BrowserShortcutServiceFactory::service=&shortcuts;
  shortcuts.commands={{IDC_FIND,{{u"Command+F"}}},
                      {IDC_TASK_MANAGER_SHORTCUT,{{u"Shift+Escape"}}},
                      {IDC_COPY_OR_INSPECT_SHORTCUT,{{u"Command+Shift+C"}}},
                      {IDC_CTRL_S_SHORTCUT,{{u"Command+S"}}}};
  assert(get(IDC_FIND).shortcut==u"Command+F");
  shortcuts.commands[0].accelerators[0].display_text=u"Custom+F";
  assert(get(IDC_FIND).shortcut==u"Custom+F");
  shortcuts.commands[0].accelerators.clear();
  assert(get(IDC_FIND).shortcut.empty());  // Removed bindings stay removed.
  assert(get(IDC_TASK_MANAGER).shortcut==u"Shift+Escape");
  assert(get(IDC_DEV_TOOLS_INSPECT).shortcut==u"Command+Shift+C");
  assert(get(IDC_COPY_URL).shortcut.empty());
  browser.profile.prefs.copy=true;
  assert(get(IDC_COPY_URL).shortcut==u"Command+Shift+C");
  assert(get(IDC_DEV_TOOLS_INSPECT).shortcut.empty());
  layout.zen=true;layout.layout=2;
  browser.profile.prefs.collapse=true;
  assert(get(kPinSidebar).shortcut==u"Command+S");
  assert(get(IDC_SAVE_PAGE).shortcut.empty());
  layout.zen=false;vertical.display=true;
  browser.profile.prefs.collapse=false;
  assert(get(IDC_SAVE_PAGE).shortcut==u"Command+S");
  browser.strip.active_present=false;assert(find(u"/").empty());
  browser.strip.active_present=true;browser.type=BrowserWindowInterface::Type::TYPE_APP;
  assert(find(u"/").empty());assert(!CommandForId(nullptr,IDC_NEW_TAB));
  std::cout<<"PASS: production command catalogue, symbols, aliases, scope, policy/availability rechecks, single-pane pin/mute, stale toggle rejection, layout state, slash vs double-slash/greater-than prefixes, recency/frequency within match bands, stable usage keys, saturation and Incognito read-only history, active/custom/removed shortcuts and contextual wrapper routing, missing/unsupported windows\n";
}
'''
with tempfile.TemporaryDirectory(prefix='lune-command-actions-') as temporary:
    source = Path(temporary) / 'actions.cc'
    binary = Path(temporary) / 'actions'
    source.write_text(program)
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-arch', args.arch,
                    str(source), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
