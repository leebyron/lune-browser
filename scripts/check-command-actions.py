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
for message in ET.parse(args.source / 'chrome/app/settings_strings.grdp').iter('message'):
    if message.attrib.get('name') == 'IDS_OLDER_TABS_KEEP':
        labels[message.attrib['name']] = ''.join(message.itertext()).strip()
commands = sorted(set(re.findall(r'\bIDC_[A-Z_]+', registry)))
label_ids = sorted(labels)
definitions = '\n'.join(f'constexpr int {name} = {n};'
                        for n, name in enumerate(commands + label_ids, 1))
label_switch = '\n'.join(f'case {name}: return u"{labels[name]}";' for name in label_ids)
symbol_constants = (ui / 'helium_command_symbols.h').read_text()
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
#include <functional>
#include <tuple>
#include <iterator>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <string>
#include <vector>
''' + definitions + r'''
namespace base {
template<class T> struct WeakPtr {
  T* value;T* get() const{return value;}T* operator->() const{return value;}
  explicit operator bool() const{return value;}
};
struct OnceClosure {
  std::function<void()> fn;
  void Run(){auto once=std::move(fn);once();}
};
template<class F,class... A> OnceClosure BindOnce(F fn,A... args) {
  return {[fn,args...]() mutable {fn(args...);}};
}
struct TimeDelta {int seconds;};
TimeDelta Seconds(int seconds){return {seconds};}
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
namespace media_session::mojom {
enum class MediaSessionAction {kPlay,kPause,kPreviousTrack,kNextTrack,kSeekBackward,kSeekForward,kStop,kSkipAd,kEnterPictureInPicture,kExitPictureInPicture};
enum class MediaPlaybackState {kPlaying,kPaused};
enum class MediaPictureInPictureState {kNotInPictureInPicture,kInPictureInPicture};
constexpr int kDefaultSeekTimeSeconds=5;
struct MediaSessionInfo {
  enum class SessionState {kActive,kSuspended,kInactive};
  SessionState state=SessionState::kActive;
  bool is_controllable=true;
  MediaPlaybackState playback_state=MediaPlaybackState::kPlaying;
  MediaPictureInPictureState picture_in_picture_state=MediaPictureInPictureState::kNotInPictureInPicture;
};
}
namespace tab_groups {using TabGroupId=int;}
namespace content {class MediaSession;}
namespace content {struct WebContents {
  bool older=false,recently_audible=false,audibility_available=true;
  MediaSession* media=nullptr;
  Profile* context=nullptr;std::string request_id;
  std::u16string title=u"Media target";
  Profile* GetBrowserContext(){return context;}
  const std::u16string& GetTitle(){return title;}
  base::WeakPtr<WebContents> GetWeakPtr(){return {this};}
};}
namespace content {
class MediaSession {
 public:
  enum class SuspendType {kUI};
  media_session::mojom::MediaSessionInfo info;
  bool info_available=true;
  std::vector<media_session::mojom::MediaSessionAction> actions;
  std::string executed;int seek_seconds=0;
  inline static std::map<std::string,WebContents*> targets;
  struct RequestId {std::string value;std::string ToString() const{return value;}};
  static RequestId GetRequestIdFromWebContents(WebContents* page){
    if(page->request_id.empty())page->request_id="session-"+std::to_string(targets.size()+1);
    targets[page->request_id]=page;return {page->request_id};
  }
  static WebContents* GetWebContentsFromRequestId(const std::string& id){
    auto it=targets.find(id);return it==targets.end()?nullptr:it->second;
  }
  static MediaSession* GetIfExists(WebContents* page){assert(page);return page->media;}
  auto GetMediaSessionInfoSync(){return info_available?std::make_unique<media_session::mojom::MediaSessionInfo>(info):nullptr;}
  auto GetMediaSessionActionsSync() const{return actions;}
  void Resume(SuspendType){executed="play";}
  void Suspend(SuspendType){executed="pause";}
  void PreviousTrack(){executed="previous";}
  void NextTrack(){executed="next";}
  void Seek(base::TimeDelta time){executed="seek";seek_seconds=time.seconds;}
  void Stop(SuspendType){executed="stop";}
  void SkipAd(){executed="skip ad";}
  void EnterPictureInPicture(){executed="enter pip";}
  void ExitPictureInPicture(){executed="exit pip";}
};
}
struct MediaNotificationService {
  struct Manager {
    std::vector<std::string> ids;
    auto GetActiveItemIds(){return ids;}
  } manager;
  Manager* media_item_manager(){return &manager;}
};
struct MediaNotificationServiceFactory {
  inline static MediaNotificationService* service=nullptr;
  static MediaNotificationService* GetForProfile(Profile*){return service;}
};
struct RecentlyAudibleHelper {
  content::WebContents* page;
  static RecentlyAudibleHelper* FromWebContents(content::WebContents* page){
    static RecentlyAudibleHelper helper;helper.page=page;
    return page->audibility_available?&helper:nullptr;
  }
  bool WasRecentlyAudible(){return page->recently_audible;}
};
namespace tabs {
struct OlderTabsController {
  bool enabled=true;int kept=0;
  bool IsEnabled(){return enabled;}
  static bool IsOlder(const content::WebContents* page){return page&&page->older;}
  void Keep(content::WebContents* page){++kept;page->older=false;}
};
}
struct TabStripModel {
  tabs::OlderTabsController cleanup;
  tabs::OlderTabsController* older_tabs_controller(){return &cleanup;}
  enum {CommandTogglePinned,CommandToggleSiteMuted,CommandToggleGrouped,CommandRemoveFromGroup};
  static constexpr int kNoTab=-1;
  bool groups_supported=true,group_enabled=true,confirm_removal=false;
  std::optional<int> group[2];int editor=0;std::vector<int> marked;
  base::OnceClosure pending;
  bool SupportsTabGroups(){return groups_supported;}
  std::optional<int> GetTabGroupForTab(int i){return group[i];}
  int AddToNewGroup(std::vector<int> indices){assert(indices==std::vector<int>{0});group[0]=42;return 42;}
  void OpenTabGroupEditor(int id){editor=id;}
  std::vector<int> GetGroupsDestroyedFromRemovingIndices(std::vector<int> indices){assert(indices==std::vector<int>{0});return confirm_removal?std::vector<int>{*group[0]}:std::vector<int>{};}
  void MarkTabGroupsForClosing(std::vector<int> ids){marked=ids;}
  int GetIndexOfWebContents(content::WebContents* target){return active_present && target==&page?0:kNoTab;}
  void RemoveFromGroup(std::vector<int> indices){assert(indices==std::vector<int>{0});group[0].reset();}
  TabStripModel* delegate(){return this;}
  void OnRemovingAllTabsFromGroups(std::vector<int> ids,base::OnceClosure callback){assert(ids==marked);pending=std::move(callback);}
  bool active_present=true,pin_enabled=true,mute_enabled=true;
  bool pinned[2]={false,true},muted[2]={false,false};
  content::WebContents page;
  int active_index(){return 0;}
  content::WebContents* GetActiveWebContents(){return active_present?&page:nullptr;}
  bool IsContextMenuCommandEnabled(int i,int command){assert(i==0);return command==CommandTogglePinned?pin_enabled:command==CommandToggleSiteMuted?mute_enabled:group_enabled;}
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
  base::WeakPtr<BrowserWindowInterface> GetWeakPtr(){return {this};}
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
  std::u16string title,shortcut,description;std::string symbol_name,media_request_id;
};
namespace helium_command_bar_model {
constexpr int kPinSidebar=-1,kMediaPlayPause=-2,kMediaPictureInPicture=-3,kMediaPreviousTrack=-4,kMediaNextTrack=-5,kMediaSeekBackward=-6,kMediaSeekForward=-7,kMediaStop=-8,kMediaSkipAd=-9,kKeepOlderTab=-10;
constexpr int kScoreExact=140,kScorePrefix=70,kScoreWord=45,kScoreSubstring=20;
''' + function(model, 'bool IsWordBoundary(') + '\n' + function(model, 'int ScoreText(') + '\n}\n' + symbol_constants + body + mode_helpers + r'''
int main() {
  using namespace helium_command_bar_model;
  assert(std::size(kCommands)==54);
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
  browser.strip.page.context=&browser.profile;
  auto find=[&](const std::u16string& q,bool scope=true){return CommandsForQuery(&browser,q,scope);};
  auto get=[&](int command){auto item=CommandForId(&browser,command);assert(item);return *item;};
  auto has=[&](const auto& rows,int command){return std::ranges::any_of(rows,[&](const auto& r){return r.command==command;});};
  assert(!CommandForId(&browser,kKeepOlderTab));
  assert(!has(find(u"keep tab",false),kKeepOlderTab));
  browser.strip.page.older=true;
  auto keep=get(kKeepOlderTab);assert(keep.title==u"Keep Tab");
  assert(has(find(u"keep tab",false),kKeepOlderTab));
  assert(has(find(u"/keep tab"),kKeepOlderTab));
  browser.strip.cleanup.enabled=false;
  assert(!CommandForId(&browser,kKeepOlderTab));
  assert(!ExecutePaletteCommand(&browser,keep));
  browser.strip.cleanup.enabled=true;browser.strip.page.older=false;
  assert(!ExecutePaletteCommand(&browser,keep));
  browser.strip.page.older=true;
  assert(ExecutePaletteCommand(&browser,keep));
  assert(browser.strip.cleanup.kept==1&&!browser.strip.page.older);
  assert(!CommandForId(&browser,kKeepOlderTab));
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
  assert(get(IDC_HOME).symbol_name=="house");
  assert(get(IDC_CREATE_NEW_TAB_GROUP).symbol_name=="folder.badge.plus");
  assert(find(u"/ungroup tab").empty());
  auto group=get(IDC_WINDOW_GROUP_TAB);
  assert(group.title==u"Group Tab" && group.symbol_name=="folder");
  browser.strip.group[1]=99;  // Unrelated selection must remain untouched.
  assert(ExecutePaletteCommand(&browser,group));
  assert(browser.strip.group[0]==42 && browser.strip.group[1]==99 && browser.strip.editor==42);
  assert(!ExecutePaletteCommand(&browser,group));  // Stale Group cannot remove.
  auto remove=get(IDC_WINDOW_GROUP_TAB);
  assert(remove.title==u"Remove Tab from Group" && remove.symbol_name=="folder");
  assert(find(u"/ungroup tab")[0].command==IDC_WINDOW_GROUP_TAB);
  assert(ExecutePaletteCommand(&browser,remove));
  assert(!browser.strip.group[0] && browser.strip.group[1]==99);
  browser.strip.group[0]=42;browser.strip.confirm_removal=true;
  assert(ExecutePaletteCommand(&browser,get(IDC_WINDOW_GROUP_TAB)));
  assert(browser.strip.group[0]==42 && browser.strip.marked==std::vector<int>{42});
  browser.strip.pending.Run();assert(!browser.strip.group[0]);
  browser.strip.group[0]=42;
  assert(ExecutePaletteCommand(&browser,get(IDC_WINDOW_GROUP_TAB)));
  browser.strip.group[0]=43;  // Async confirmation cannot redirect to another group.
  browser.strip.pending.Run();assert(browser.strip.group[0]==43);
  browser.strip.group[0].reset();browser.strip.group[1].reset();browser.strip.confirm_removal=false;
  browser.strip.groups_supported=false;
  assert(!CommandForId(&browser,IDC_WINDOW_GROUP_TAB));
  assert(!CommandForId(&browser,IDC_CREATE_NEW_TAB_GROUP));
  browser.strip.groups_supported=true;browser.strip.group_enabled=false;
  assert(!CommandForId(&browser,IDC_WINDOW_GROUP_TAB));
  browser.strip.group_enabled=true;

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
  // Silent tabs offer no Mute action; audibility belongs to the active tab.
  content::WebContents other_media_tab;other_media_tab.recently_audible=true;
  assert(!CommandForId(&browser,IDC_WINDOW_MUTE_SITE));
  browser.strip.page.recently_audible=true;
  auto mute=get(IDC_WINDOW_MUTE_SITE);
  browser.strip.page.recently_audible=false;
  assert(!ExecutePaletteCommand(&browser,mute)&&!browser.strip.muted[0]);
  browser.strip.page.recently_audible=true;
  assert(ExecutePaletteCommand(&browser,mute));
  assert(browser.strip.muted[0]&&!browser.strip.muted[1]);
  browser.strip.page.recently_audible=false;
  auto unmute=get(IDC_WINDOW_MUTE_SITE);assert(unmute.title==u"Unmute Site");
  assert(!ExecutePaletteCommand(&browser,mute));
  assert(ExecutePaletteCommand(&browser,unmute));
  assert(!CommandForId(&browser,IDC_WINDOW_MUTE_SITE));
  browser.strip.page.recently_audible=true;
  browser.strip.page.audibility_available=false;
  assert(!CommandForId(&browser,IDC_WINDOW_MUTE_SITE));
  browser.strip.page.audibility_available=true;
  // Media capabilities belong to the invoking tab, never another session.
  using Action=media_session::mojom::MediaSessionAction;
  using Playback=media_session::mojom::MediaPlaybackState;
  using Pip=media_session::mojom::MediaPictureInPictureState;
  using State=media_session::mojom::MediaSessionInfo::SessionState;
  content::MediaSession media,other_media;
  other_media_tab.media=&other_media;other_media.actions={Action::kPlay,Action::kPause};
  for(int id=kMediaPlayPause;id>=kMediaSkipAd;--id)assert(!CommandForId(&browser,id));
  browser.strip.page.media=&media;
  assert(!CommandForId(&browser,kMediaPlayPause));
  media.actions={Action::kPlay,Action::kPause};
  auto pause=get(kMediaPlayPause);assert(pause.title==u"Pause Media"&&pause.symbol_name=="pause.fill");
  assert(ExecutePaletteCommand(&browser,pause)&&media.executed=="pause");
  media.info.playback_state=Playback::kPaused;media.info.state=State::kSuspended;
  assert(!ExecutePaletteCommand(&browser,pause));
  auto play=get(kMediaPlayPause);assert(play.title==u"Play Media"&&play.symbol_name=="play.fill");
  assert(ExecutePaletteCommand(&browser,play)&&media.executed=="play");
  media.actions.clear();assert(!ExecutePaletteCommand(&browser,play));
  media.actions={Action::kPlay};media.info.is_controllable=false;
  assert(!CommandForId(&browser,kMediaPlayPause));
  media.info.is_controllable=true;media.info.state=State::kInactive;
  assert(!CommandForId(&browser,kMediaPlayPause));
  media.info.state=State::kActive;media.info_available=false;
  assert(!CommandForId(&browser,kMediaPlayPause));media.info_available=true;
  media.actions={Action::kEnterPictureInPicture};
  auto enter_pip=get(kMediaPictureInPicture);assert(ExecutePaletteCommand(&browser,enter_pip)&&media.executed=="enter pip");
  media.info.picture_in_picture_state=Pip::kInPictureInPicture;
  assert(!ExecutePaletteCommand(&browser,enter_pip));
  media.actions={Action::kExitPictureInPicture};
  auto exit_pip=get(kMediaPictureInPicture);assert(exit_pip.title==u"Exit Picture in Picture");
  assert(ExecutePaletteCommand(&browser,exit_pip)&&media.executed=="exit pip");
  // PiP availability can exist for video without controllable audio.
  media.info.is_controllable=false;assert(CommandForId(&browser,kMediaPictureInPicture));
  media.info.is_controllable=true;
  struct MediaCase {int id;Action action;const char* result;};
  for(auto test:std::vector<MediaCase>{{kMediaPreviousTrack,Action::kPreviousTrack,"previous"},{kMediaNextTrack,Action::kNextTrack,"next"},{kMediaSeekBackward,Action::kSeekBackward,"seek"},{kMediaSeekForward,Action::kSeekForward,"seek"},{kMediaStop,Action::kStop,"stop"},{kMediaSkipAd,Action::kSkipAd,"skip ad"}}){
    media.actions={test.action};auto item=get(test.id);
    assert(ExecutePaletteCommand(&browser,item)&&media.executed==test.result);
    if(test.id==kMediaSeekBackward)assert(media.seek_seconds==-5);
    if(test.id==kMediaSeekForward)assert(media.seek_seconds==5);
    media.actions.clear();assert(!ExecutePaletteCommand(&browser,item));
    media.actions={test.action};media.info.state=State::kInactive;
    assert(!CommandForId(&browser,test.id));media.info.state=State::kActive;
  }
  media.actions={Action::kSeekBackward,Action::kSeekForward};
  const auto skip_results=find(u"/skip");
  assert(has(skip_results,kMediaSeekBackward) && has(skip_results,kMediaSeekForward));
  assert(find(u"/skip back")[0].command==kMediaSeekBackward);
  assert(find(u"/skip ahead")[0].command==kMediaSeekForward);
  media.actions.clear();
  assert(!has(find(u"/skip"),kMediaSeekBackward) && !has(find(u"/skip"),kMediaSeekForward));
  browser.strip.page.media=nullptr;assert(!ExecutePaletteCommand(&browser,exit_pip));
  // The toolbar supplies background candidates; the current playing tab wins.
  MediaNotificationService notifications;
  MediaNotificationServiceFactory::service=&notifications;
  other_media_tab.context=&browser.profile;other_media_tab.title=u"Background audio";
  other_media.actions={Action::kPlay,Action::kPause,Action::kSeekForward};
  const auto background_id=content::MediaSession::GetRequestIdFromWebContents(&other_media_tab).ToString();
  notifications.manager.ids={"cast-without-a-tab",background_id};
  auto background_pause=get(kMediaPlayPause);
  assert(background_pause.media_request_id==background_id && background_pause.description==u"Background audio");
  assert(ExecutePaletteCommand(&browser,background_pause) && other_media.executed=="pause");
  media.actions={Action::kPlay,Action::kPause};media.info.playback_state=Playback::kPlaying;
  media.info.state=State::kActive;browser.strip.page.media=&media;
  const auto foreground_pause=get(kMediaPlayPause);
  assert(foreground_pause.media_request_id!=background_id);
  assert(!ExecutePaletteCommand(&browser,background_pause));  // Do not retarget a selected row.
  assert(ExecutePaletteCommand(&browser,foreground_pause) && media.executed=="pause");
  assert(!CommandForId(&browser,kMediaSeekForward));  // One target; no capability borrowing.
  media.info.playback_state=Playback::kPaused;
  assert(get(kMediaPlayPause).media_request_id==background_id);  // Playing background beats paused current.
  Profile foreign_profile;content::WebContents foreign_page;content::MediaSession foreign_media;
  foreign_page.context=&foreign_profile;foreign_page.media=&foreign_media;
  foreign_media.actions={Action::kPause};
  const auto foreign_id=content::MediaSession::GetRequestIdFromWebContents(&foreign_page).ToString();
  notifications.manager.ids={foreign_id,background_id};
  assert(get(kMediaPlayPause).media_request_id==background_id);  // Keep profile/Incognito boundaries.
  const auto captured=get(kMediaPlayPause);
  content::MediaSession::targets.erase(background_id);
  assert(!ExecutePaletteCommand(&browser,captured));  // Closed background cannot redirect to paused foreground.
  notifications.manager.ids={foreign_id};browser.strip.page.media=nullptr;
  assert(!CommandForId(&browser,kMediaPlayPause));
  MediaNotificationServiceFactory::service=nullptr;

  assert(get(IDC_FULLSCREEN).title==u"Enter Fullscreen");browser.window.fullscreen=true;
  assert(get(IDC_FULLSCREEN).title==u"Exit Fullscreen");
  assert(!CommandForId(&browser,IDC_BROWSER_LAYOUT_VERTICAL_RIGHT));
  layout.layout=2;
  assert(find(u"/move tabs to left")[0].command==IDC_BROWSER_LAYOUT_VERTICAL_RIGHT);
  assert(find(u"/move tabs to right")[0].command==IDC_BROWSER_LAYOUT_VERTICAL_RIGHT);
  assert(find(u"/pin tabs")[0].command==kPinSidebar);
  assert(find(u"/unpin tabs")[0].command==kPinSidebar);
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
  shortcuts.commands.push_back({IDC_ZOOM_PLUS,{{u"⌘="}}});
  assert(get(IDC_ZOOM_PLUS).shortcut==u"⌘+");
  shortcuts.commands.back().accelerators[0].display_text=u"⌘⇧Z";
  assert(get(IDC_ZOOM_PLUS).shortcut==u"⌘⇧Z");
  shortcuts.commands.back().accelerators.clear();
  assert(get(IDC_ZOOM_PLUS).shortcut.empty());
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
  std::cout<<"PASS: production command catalogue, conditional Older Keep action and stale-state rejection, symbols, aliases, scope, policy/availability rechecks, single-pane pin/mute/grouping and deferred group confirmation, audibility gating and silent-site unmute, foreground-playing preference, toolbar-ordered background media and profile/target identity rechecks, playback/PiP/track/seek/stop/ad dispatch, stale toggle rejection, layout state, slash vs double-slash/greater-than prefixes, recency/frequency within match bands, stable usage keys, saturation and Incognito read-only history, active/custom/removed shortcuts and contextual wrapper routing, missing/unsupported windows\n";
}
'''
with tempfile.TemporaryDirectory(prefix='lune-command-actions-') as temporary:
    source = Path(temporary) / 'actions.cc'
    binary = Path(temporary) / 'actions'
    source.write_text(program)
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-arch', args.arch,
                    str(source), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
