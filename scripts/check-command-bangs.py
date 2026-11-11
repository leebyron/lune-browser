#!/usr/bin/env python3
"""Compile production bang matching/ranking/usage with small service/pref doubles."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
args = parser.parse_args()
ui = args.source / 'chrome/browser/ui/helium'
model = (ui / 'helium_command_bar_model.cc').read_text()
header = (ui / 'helium_command_bar_model.h').read_text()

def function(signature, text=model):
    start = text.index(signature)
    opening = text.index('{', start)
    depth, end = 1, opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

controller = (ui / 'helium_command_bar_controller.cc').read_text()
start = controller.index('    case HeliumCommandBarItem::Type::kBang:')
end = controller.index('    case HeliumCommandBarItem::Type::kSiteSearch:', start)
submit = function('void HeliumCommandBarController::SubmitBangSearch()', controller).replace('HeliumCommandBarController::', 'Activation::')
enter_scope = function('void HeliumCommandBarController::EnterScope(', controller).replace('HeliumCommandBarController::', 'Activation::')
backspace = function('void HeliumCommandBarController::OnBackspacePressed()', controller).replace('HeliumCommandBarController::', 'Activation::')
collect = controller[controller.index('    const history::QueryResults* history_rows) {') + len('    const history::QueryResults* history_rows) {'):]
collect = collect[:collect.index('  using namespace helium_command_bar_model;')]
activation = controller[start:end].replace('    case HeliumCommandBarItem::Type::kBang:', '')

views = [(ui / name).read_text() for name in
         ['helium_command_bar_view.cc', 'helium_command_bar_view_mac.mm']]
def selection_body(text):
    begin = text.index('  std::optional<HeliumCommandBarItem> selected;')
    end = text.index('  displayed_items_ = items;', begin)
    return text[begin:end] + '  displayed_items_ = items;'
selection = selection_body(views[1])

hover_start = views[1].index('    row.onHover = ^(NSInteger index) {')
hover_end = views[1].index('    };', hover_start) + len('    };')
hover = views[1][hover_start:hover_end].replace('row.onHover = ^(NSInteger index)', 'auto hover = [&](size_t index)').replace('NSEvent.mouseLocation', 'current_mouse')

assert selection == selection_body(views[0])
reset_selection = function('void HeliumCommandBarView::ResetSelection()', views[1]).replace('HeliumCommandBarView::', 'ResultSelection::')
set_selected = function('void HeliumCommandBarView::SetSelected(', views[1]).replace('HeliumCommandBarView::', 'ResultSelection::').replace('native_->pane.rows.count', 'displayed_items_.size()')

item = header[header.index('struct HeliumCommandBarItem {'):header.index('namespace helium_command_bar_model')]
program = r'''
#include <algorithm>
#include <cassert>
#include <chrono>
#include <iostream>
#include <map>
#include <memory>
#include <optional>
#include <set>
#include <string>
#include <string_view>
#include <vector>
namespace base {
struct Time {
  double seconds = 2000000000;
  static Time Now() { return {}; }
  double InSecondsFSinceUnixEpoch() const { return seconds; }
};
enum TrimPositions { TRIM_ALL, TRIM_LEADING };
constexpr char16_t kWhitespaceUTF16[] = u" \t\r\n";
std::u16string_view TrimWhitespace(std::u16string_view text, TrimPositions pos) {
  auto begin = text.find_first_not_of(kWhitespaceUTF16);
  if (begin == text.npos) return {};
  auto end = pos == TRIM_ALL ? text.find_last_not_of(kWhitespaceUTF16) + 1 : text.size();
  return text.substr(begin, end - begin);
}
std::u16string CollapseWhitespace(std::u16string_view text, bool) {
  text = TrimWhitespace(text, TRIM_ALL);
  std::u16string result;
  for (auto c : text) {
    bool space = std::u16string_view(kWhitespaceUTF16).find(c) != text.npos;
    if (!space || result.empty() || result.back() != u' ') result += space ? u' ' : c;
  }
  return result;
}
std::u16string ToLowerASCII(std::u16string_view text) {
  std::u16string result(text);
  for (auto& c : result) if (c >= u'A' && c <= u'Z') c += 32;
  return result;
}
std::string UTF16ToUTF8(std::u16string_view s) { return {s.begin(), s.end()}; }
std::u16string UTF8ToUTF16(std::string_view s) { return {s.begin(), s.end()}; }
// Stand-in for base's separately tested bounded edit-distance primitive.
size_t LevenshteinDistance(std::u16string_view a, std::u16string_view b, size_t) {
  std::vector<size_t> row(b.size() + 1);
  for (size_t i = 0; i < row.size(); ++i) row[i] = i;
  for (size_t i = 0; i < a.size(); ++i) {
    size_t previous = row[0]; row[0] = i + 1;
    for (size_t j = 0; j < b.size(); ++j) {
      size_t old = row[j + 1];
      row[j + 1] = std::min({row[j + 1] + 1, row[j] + 1, previous + (a[i] != b[j])});
      previous = old;
    }
  }
  return row.back();
}
struct DictValue;
struct Value {
  std::shared_ptr<DictValue> dict;
  std::optional<int> integer;
  std::optional<double> number;
  const DictValue* GetIfDict() const { return dict.get(); }
};
struct DictValue : std::map<std::string, Value> {
  const DictValue* FindDict(const std::string& k) const {
    auto i = find(k); return i == end() ? nullptr : i->second.dict.get();
  }
  DictValue* EnsureDict(const std::string& k) {
    auto& v = (*this)[k]; if (!v.dict) v.dict = std::make_shared<DictValue>();
    return v.dict.get();
  }
  std::optional<int> FindInt(const std::string& k) const {
    auto i = find(k); return i == end() ? std::nullopt : i->second.integer;
  }
  std::optional<double> FindDouble(const std::string& k) const {
    auto i = find(k); return i == end() ? std::nullopt : i->second.number;
  }
  void Set(const std::string& k, int n) { (*this)[k].integer = n; }
  void Set(const std::string& k, double n) { (*this)[k].number = n; }
  void Remove(const std::string& k) { erase(k); }
};
}
namespace prefs { constexpr char kHeliumCommandBarBangUsage[] = "usage"; }
struct PrefService {
  base::DictValue usage;
  const base::DictValue& GetDict(const char*) const { return usage; }
};
struct Profile {
  bool private_mode = false;
  PrefService prefs;
  bool IsOffTheRecord() const { return private_mode; }
  PrefService* GetPrefs() { return &prefs; }
};
struct ScopedDictPrefUpdate {
  PrefService* prefs;
  ScopedDictPrefUpdate(PrefService* p, const char*) : prefs(p) {}
  base::DictValue* operator->() { return &prefs->usage; }
  base::DictValue& operator*() { return prefs->usage; }
};
struct GURL {
  std::string value;
  bool is_valid() const { return !value.empty(); }
  bool operator==(const GURL&) const = default;
};
struct TemplateURL {
  std::u16string trigger, name;
  bool active = true, searchable = true;
  const std::u16string& keyword() const { return trigger; }
  const std::u16string& short_name() const { return name; }
  GURL favicon_url() const { return {}; }
  bool CanBeUsedForKeywordMatching() const { return active; }
  const TemplateURL& url_ref() const { return *this; }
  bool SupportsReplacement(int) const { return searchable; }
};
struct TemplateURLService {
  std::vector<TemplateURL*> entries;
  std::vector<TemplateURL*> GetTemplateURLs() { return entries; }
  TemplateURL* GetTemplateURLForKeyword(const std::u16string& keyword) {
    for (auto* p : entries) if (p->trigger == keyword) return p;
    return nullptr;
  }
  int search_terms_data() { return 0; }
};
''' + item + '\nconstexpr size_t kMaxResults = 9;\n' + '\n'.join(
    re.findall(r'constexpr int kScore\w+ = [^;]+;', model)) + '\n' + '\n'.join(
    function(f) for f in [
        'bool IsWordBoundary(', 'int ScoreText(', 'const TemplateURL* EngineForKeyword(',
        'std::optional<HeliumCommandBarItem> SiteSearchHintForQuery(',
        'int ScoreBangText(', 'int BangUsageScore(', 'int FamiliarBangScore(',
        'std::vector<HeliumCommandBarItem> BangsForQuery(', 'void RecordBangUse(',
         'bool SameItem(', 'void SortAndCap(']) + r'''
namespace helium_command_bar_model {
bool EngineOwnsKeyword(TemplateURLService* service, const std::string& keyword) {
  return EngineForKeyword(service, keyword);
}
using ::RecordBangUse;
using ::SameItem;
std::optional<GURL> BuildSiteSearchUrl(TemplateURLService* service,
    const std::string& keyword, const std::u16string& query) {
  if (!EngineForKeyword(service, keyword) || query.empty()) return std::nullopt;
  return GURL{keyword + "|" + base::UTF16ToUTF8(query)};
}
}
struct Browser {
  Profile profile;
  Profile* GetProfile() { return &profile; }
};
struct TemplateURLServiceFactory {
  static inline TemplateURLService* service = nullptr;
  static TemplateURLService* GetForProfile(Profile*) { return service; }
};
struct Activation {
  Browser browser;
  Browser* browser_ = &browser;
  struct View {
    std::u16string text;
    std::optional<size_t> caret;
    void SetInputText(const std::u16string& value,
                      std::optional<size_t> position = std::nullopt) {
      text = value; caret = position;
    }
  } view;
  View* view_ = &view;
  std::string scope_keyword_;
  bool scope_keyword_was_typed_ = false;
  std::u16string last_query_;
  GURL opened;
  bool closed = false;
  void OpenUrl(const GURL& url) { opened = url; }
  void HideSoon() { closed = true; }
  void SubmitBangSearch();
  void EnterScope(const std::string& keyword,
                  const std::u16string& query = {},
                  bool keyword_was_typed = true);
  void OnBackspacePressed();
  void OnQueryChanged(const std::u16string& query) { last_query_ = query; }
  void Activate(const HeliumCommandBarItem& item) {
''' + activation + r'''
  }
};
''' + submit + enter_scope + backspace + r'''
std::vector<HeliumCommandBarItem> ScopeRows(std::string scope_keyword_) {
''' + collect + r'''
  return {HeliumCommandBarItem{}};
}
struct ResultSelection {
  std::vector<HeliumCommandBarItem> displayed_items_;
  size_t selected_ = 0;
  bool selection_is_explicit_ = false;
  void UpdateRowHighlight() {}
  void ResetSelection();
  void SetSelected(size_t index);
  void Apply(const std::vector<HeliumCommandBarItem>& items) {
''' + selection + r'''
  }
};
''' + reset_selection + set_selected + r'''
int main() {
  using T = HeliumCommandBarItem::Type;
  Profile profile;
  TemplateURL github{u"!gh", u"GitHub"}, wikipedia{u"!w", u"Wikipedia"};
  TemplateURL wiki_alias{u"!wiki", u"Wikipedia"};
  TemplateURL wiki_alias2{u"!wikipedia", u"Wikipedia"};
  TemplateURL custom{u"!custom", u"Custom Site"}, disabled{u"!disabled", u"Disabled", false};
  TemplateURL unsupported{u"!unsupported", u"Unsupported", true, false};
  TemplateURL overridden{u"!gh", u"Wrong provider"}, ordinary{u"github.com", u"GitHub"};
  TemplateURLService service{{&github, &wikipedia, &custom, &disabled, &unsupported, &overridden, &ordinary, &wiki_alias, &wiki_alias2}};
  auto find = [&](std::u16string text) { return BangsForQuery(&service, profile.GetPrefs(), text); };
  assert(find(u"").empty() && find(u"unrelated zebra query").empty());
  assert(BangsForQuery(nullptr, profile.GetPrefs(), u"!").empty());
  auto popular = find(u"!");
  assert(popular.size() == 3 && popular[0].site_keyword == "!w");
  for (auto query : {u"gh", u"git", u"github", u"githb", u"gihtub", u"!githb", u"!GITHUB"}) {
    auto rows = find(query);
    assert(!rows.empty() && rows[0].site_keyword == "!gh");
    assert(rows[0].type == T::kBang && rows[0].site_query.empty());
  }
  assert(find(u"disabled").empty() && find(u"unsupported").empty());
  auto pasted = find(u" !GITHB  Cats and Dogs  ");
  assert(pasted.size() == 1 && pasted[0].site_query == u"Cats and Dogs");
  assert(find(u"!w cats")[0].site_query == u"cats");
  assert(find(u"wiki").size() == 1 && find(u"!wiki").size() == 1);
  assert(find(u"wikipedia")[0].site_keyword == "!w");
  RecordBangUse(&profile, "!wikipedia");
  assert(find(u"wiki").size() == 1);
  assert(find(u"wikipedia")[0].site_keyword == "!wikipedia");
  TemplateURLServiceFactory::service = &service;
  Activation action;
  action.Activate(pasted[0]);
  assert(action.scope_keyword_ == "!gh" && action.last_query_ == u"Cats and Dogs");
  action.Activate(find(u"wiki")[0]);
  assert(action.scope_keyword_ == "!wiki" && action.last_query_.empty());
  github.active = false;
  action.Activate(pasted[0]);
  assert(action.scope_keyword_ == "!wiki");  // Stale completion cannot apply a removed scope.
  github.active = true;
  assert(ScopeRows("!w").empty() && ScopeRows("!anything").empty());
  assert(ScopeRows("tab").size() == 1 && ScopeRows("").size() == 1);
  action.SubmitBangSearch();
  assert(!action.opened.is_valid() && !action.closed);  // Empty scoped Enter.
  action.last_query_ = u"Cats and Dogs";
  action.SubmitBangSearch();
  assert(action.opened.value == "!wiki|Cats and Dogs" && action.closed);
  assert(action.browser.profile.prefs.usage.FindDict("!wiki")->FindInt("count") == 1);
  action.opened = {}; action.closed = false;
  action.scope_keyword_ = "!missing";
  action.SubmitBangSearch();
  assert(!action.opened.is_valid() && !action.closed);
  action.scope_keyword_ = "github.com";
  action.SubmitBangSearch();
  assert(!action.opened.is_valid() && !action.closed);
  Activation removal;
  removal.Activate(find(u"wiki")[0]);
  assert(!removal.scope_keyword_was_typed_);
  removal.OnBackspacePressed();
  assert(removal.scope_keyword_.empty() && removal.last_query_.empty());
  assert(removal.view.text.empty() && removal.view.caret == 0);
  removal.EnterScope("!w");  // Explicit trigger followed by Space.
  assert(removal.scope_keyword_was_typed_);
  removal.OnBackspacePressed();
  assert(removal.last_query_ == u"!w" && removal.view.caret == 2);
  removal.EnterScope("!w", u"Cats and Dogs");
  removal.OnBackspacePressed();
  assert(removal.last_query_ == u"!w Cats and Dogs" && removal.view.caret == 2);
  removal.Activate(pasted[0]);  // A completion with retained terms.
  assert(!removal.scope_keyword_was_typed_);
  removal.OnBackspacePressed();
  assert(removal.last_query_ == u"Cats and Dogs" && removal.view.caret == 0);
  removal.Activate(find(u"wiki")[0]);
  removal.OnQueryChanged(u"new terms");
  removal.OnBackspacePressed();
  assert(removal.last_query_ == u"new terms" && removal.view.caret == 0);
  auto mixed = find(u"github");
  HeliumCommandBarItem search{}, tab{}, top_hit{}, history{};
  search.type = T::kSearch; search.score = kScoreSearch;
  tab.type = T::kTab; tab.score = kScorePrefix + kScoreTabBoost;
  top_hit.type = T::kNavigationSuggestion; top_hit.score = 60;
  history.type = T::kHistory; history.score = kScorePrefix;
  mixed.insert(mixed.end(), {search, tab, top_hit, history});
  SortAndCap(mixed);
  assert(mixed[0].type == T::kSearch && mixed[1].type == T::kTab);
  assert(mixed[2].type == T::kHistory && mixed[3].type == T::kNavigationSuggestion);
  assert(mixed[4].type == T::kBang);
  auto explicit_rows = find(u"!github");
  explicit_rows.insert(explicit_rows.end(), {search, tab, top_hit});
  SortAndCap(explicit_rows);
  assert(explicit_rows[0].type == T::kBang);
  // Automatic selection follows ranking as sources arrive; explicit choices
  // survive asynchronous reordering, but never leak into a newly typed query.
  ResultSelection selection_state;
  auto bang = find(u"wiki")[0];
  selection_state.Apply({bang});
  selection_state.Apply({search, bang});
  assert(selection_state.selected_ == 0 && !selection_state.selection_is_explicit_);
  selection_state.SetSelected(1);
  selection_state.Apply({bang, search});
  assert(selection_state.selected_ == 0 && selection_state.selection_is_explicit_);
  selection_state.ResetSelection();
  selection_state.Apply({search, bang});
  assert(selection_state.selected_ == 0 && !selection_state.selection_is_explicit_);
  selection_state.ResetSelection();
  struct Point { int x, y; };
  const Point mouse_at_rebuild{20, 30};
  Point current_mouse = mouse_at_rebuild;
  auto NSEqualPoints = [](Point a, Point b) { return a.x == b.x && a.y == b.y; };
  auto SetSelected = [&](size_t index) { selection_state.SetSelected(index); };
''' + hover + r'''
  hover(1);  // A tracking area appears beneath a stationary pointer.
  assert(selection_state.selected_ == 0 && !selection_state.selection_is_explicit_);
  current_mouse.x += 1;
  hover(1);  // Actual pointer movement may select the completion.
  assert(selection_state.selected_ == 1 && selection_state.selection_is_explicit_);
  selection_state.SetSelected(1);
  selection_state.Apply({search});
  assert(selection_state.selected_ == 0 && !selection_state.selection_is_explicit_);
  for (int i = 0; i < 5; ++i) RecordBangUse(&profile, "!custom");
  assert(find(u"!")[0].site_keyword == "!custom");
  auto* custom_use = profile.prefs.usage.EnsureDict("!custom");
  assert(custom_use->FindInt("count") == 5);
  custom_use->Set("last_used", base::Time::Now().seconds - 86400 * 40);
  RecordBangUse(&profile, "!gh");
  assert(find(u"!")[0].site_keyword == "!gh");
  auto normal = find(u"github");
  assert(normal[0].score < kScorePrefix && normal[0].score < 60);
  profile.private_mode = true;
  RecordBangUse(&profile, "!private");
  assert(!profile.prefs.usage.FindDict("!private"));
  profile.private_mode = false;
  RecordBangUse(&profile, "github.com");
  assert(!profile.prefs.usage.FindDict("github.com"));
  RecordBangUse(&profile, "!with.dots");
  assert(profile.prefs.usage.FindDict("!with.dots"));
  for (int i = 0; i < 250; ++i) RecordBangUse(&profile, "!test" + std::to_string(i));
  assert(profile.prefs.usage.size() == 200);
  // Relevance dominates even maximum personal use: exact !gh before a prefix.
  auto* usage = profile.prefs.usage.EnsureDict("!custom");
  usage->Set("count", 999); usage->Set("last_used", base::Time::Now().seconds);
  TemplateURL prefix{u"!ghother", u"GitHub Other"}; service.entries.push_back(&prefix);
  assert(find(u"!gh")[0].site_keyword == "!gh");
  // Catalogue order cannot hide the best match or favorite beyond row nine.
  std::vector<TemplateURL> many;
  many.reserve(15000);
  for (int i = 0; i < 15000; ++i) {
    many.push_back({base::UTF8ToUTF16("!zz" + std::to_string(i)),
                    base::UTF8ToUTF16("Zebra site " + std::to_string(i))});
    service.entries.push_back(&many.back());
  }
  auto start = std::chrono::steady_clock::now();
  auto large = find(u"!");
  assert(large.size() == 9 && large[0].site_keyword == "!custom");
  auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
      std::chrono::steady_clock::now() - start).count();
  std::cout << "PASS: catalogue, plain/explicit intent, typo/case matching, website/tab priority, "
    "scope terms, completion vs typed-trigger Backspace with retained terms and caret, ranked default selection, stationary-pointer hover, explicit selection across async updates, rowless scoped submission, no scoped completions, personal frequency/recency, Incognito, literal keys, bounded history, "
    "eligibility/precedence, one completion per service, ranking before cap; 15000-entry scan " << ms << "ms\n";
}
'''
with tempfile.TemporaryDirectory(prefix='lune-command-bangs-') as temporary:
    source = Path(temporary) / 'bangs.cc'
    binary = Path(temporary) / 'bangs'
    source.write_text(program)
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-O2', '-arch', args.arch,
                    str(source), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
