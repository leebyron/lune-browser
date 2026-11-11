#!/usr/bin/env python3
"""Compile production palette ranking/selection with small URL/service-free types."""
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
score_constants = '\n'.join(re.findall(r'constexpr int kScore\w+ = [^;]+;', model))

def function(text, signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

selection = []
for name in ['helium_command_bar_view.cc', 'helium_command_bar_view_mac.mm']:
    text = (ui / name).read_text()
    start = text.index('  std::optional<HeliumCommandBarItem> selected;')
    end = text.index('  displayed_items_ = items;', start) + len('  displayed_items_ = items;')
    selection.append(text[start:end])
assert selection[0] == selection[1], 'Native and Views selection policies diverge'
item = header[header.index('struct HeliumCommandBarItem {'):header.index('namespace helium_command_bar_model')]
adapter = (ui / 'helium_command_bar_suggestions.cc').read_text()
start = adapter.index('      if (!IsRemoteSuggestion(match.type)')
end = adapter.index('      if (std::ranges::any_of', start)
predicate = adapter[start:end].replace('continue;', 'return false;')
remote_filter = r'''
namespace omnibox {
enum class AutocompleteMatchType { kSearchSuggest, kSearchSuggestEntity,
  kSearchSuggestTail, kSearchSuggestPersonalized, kNavsuggest,
  kNavsuggestPersonalized, kSearchWhatYouTyped };
}
struct AutocompleteMatch {
  omnibox::AutocompleteMatchType type;
  bool from_keyword;
  std::u16string keyword;
  GURL destination_url;
  static bool IsSearchType(omnibox::AutocompleteMatchType type) {
    return type != omnibox::AutocompleteMatchType::kNavsuggest &&
           type != omnibox::AutocompleteMatchType::kNavsuggestPersonalized;
  }
};
''' + function(adapter, 'bool IsRemoteSuggestion(') + r'''
bool AcceptMatch(const AutocompleteMatch& match,
                 const std::u16string& engine_keyword_, bool keyword_mode_) {
''' + predicate + '\nreturn true;\n}\n'
program = r'''
#include <algorithm>
#include <cassert>
#include <iostream>
#include <optional>
#include <string>
#include <vector>
struct GURL {
  std::string value;
  bool is_valid() const { return !value.empty(); }
  bool SchemeIsHTTPOrHTTPS() const {
    return value.starts_with("http://") || value.starts_with("https://");
  }
  bool operator==(const GURL&) const = default;
};
''' + remote_filter + item + '\nnamespace helium_command_bar_model {\nconstexpr size_t kMaxResults = 9;\n' + score_constants + '\n' + function(model, 'bool SameItem(') + '\n' + function(model, 'void SortAndCap(') + r'''
}
struct Selection {
  size_t selected_ = 0;
  bool selection_is_explicit_ = false;
  std::vector<HeliumCommandBarItem> displayed_items_;
  void Update(const std::vector<HeliumCommandBarItem>& items) {
''' + selection[0] + r'''
  }
};
using Item = HeliumCommandBarItem;
using Type = Item::Type;
Item Make(Type type, const char* url, int score) {
  Item item;
  item.type = type;
  item.url.value = url;
  item.score = score;
  return item;
}
int main() {
  using namespace helium_command_bar_model;
  using MatchType = omnibox::AutocompleteMatchType;
  // Navigation suggestions have no keyword string. Their origin is encoded
  // by from_keyword; rejecting an empty keyword used to remove every top hit.
  AutocompleteMatch nav{MatchType::kNavsuggest, false, u"", {"https://example.org"}};
  assert(AcceptMatch(nav, u"engine", false));
  assert(!AcceptMatch(nav, u"engine", true));
  nav.from_keyword = true;
  assert(AcceptMatch(nav, u"engine", true));
  nav.destination_url.value = "javascript:bad";
  assert(!AcceptMatch(nav, u"engine", true));
  AutocompleteMatch search{MatchType::kSearchSuggest, false, u"engine", {"https://engine/search?q=related"}};
  assert(AcceptMatch(search, u"engine", false));
  assert(!AcceptMatch(search, u"other", false));
  search.type = MatchType::kSearchWhatYouTyped;
  assert(!AcceptMatch(search, u"engine", false));
  std::vector<Item> crowded;
  for (int i = 0; i < 20; ++i) crowded.push_back(Make(Type::kTab, "tab", 100));
  crowded.push_back(Make(Type::kSearch, "search", kScoreSearch));
  SortAndCap(crowded);
  assert(crowded.size() == 9 && crowded[0].type == Type::kSearch);
  crowded.push_back(Make(Type::kUrl, "typed", kScoreUrl));
  // Test direct URL independently, as production emits one typed action.
  std::erase_if(crowded, [](const Item& i) { return i.type == Type::kSearch; });
  SortAndCap(crowded);
  assert(crowded[0].type == Type::kUrl);

  std::vector<Item> mixed = {
    Make(Type::kSearchSuggestion, "search", 60),
    Make(Type::kNavigationSuggestion, "open-tab", 59),
    Make(Type::kNavigationSuggestion, "new-site", 58),
    Make(Type::kSearchSuggestion, "related-search", 57),
    Make(Type::kTab, "open-tab", 90),
    Make(Type::kSearch, "search", kScoreSearch),
  };
  SortAndCap(mixed);
  assert(mixed.size() == 4);
  assert(mixed[0].type == Type::kSearch && mixed[1].type == Type::kTab);
  assert(mixed[2].url.value == "new-site" && mixed[3].url.value == "related-search");

  // Pasted engine scopes keep their scoped typed action above the redundant
  // default-engine search; a literal URL still takes priority over a hint.
  std::vector<Item> scoped = {
    Make(Type::kSiteSearch, "", kScoreScope),
    Make(Type::kSearch, "default-search", kScoreSearch),
    Make(Type::kSearchSuggestion, "scoped-suggestion", 60),
  };
  SortAndCap(scoped);
  assert(scoped[0].type == Type::kSiteSearch);
  scoped.push_back(Make(Type::kUrl, "explicit-url", kScoreUrl));
  std::erase_if(scoped, [](const Item& i) { return i.type == Type::kSearch; });
  SortAndCap(scoped);
  assert(scoped[0].type == Type::kUrl);

  Selection view;
  // The initial typed action remains selected and first after a higher-score
  // suggestion arrives. Enter must not require moving back up the menu.
  view.Update({Make(Type::kSearch, "search", kScoreSearch)});
  view.Update(mixed);
  assert(view.selected_ == 0 && view.displayed_items_[0].type == Type::kSearch);
  view.Update(mixed);
  view.selected_ = 3;
  view.selection_is_explicit_ = true;
  auto arriving = Make(Type::kNavigationSuggestion, "arrived", 60);
  mixed.insert(mixed.begin(), arriving);
  view.Update(mixed);
  assert(view.selected_ == 4 && view.displayed_items_[4].url.value == "related-search");
  mixed.pop_back();
  view.Update(mixed);
  assert(view.selected_ == 0);
  view.Update({});
  assert(view.selected_ == 0);
  Item scope = Make(Type::kSiteSearch, "", 100);
  Item other_scope = scope;
  scope.site_keyword = "one";
  other_scope.site_keyword = "two";
  assert(!SameItem(scope, other_scope));
  // A disappearing command cannot silently turn Enter into another action.
  Item command = Make(Type::kCommand, "", 100);
  command.command = 42;
  view.Update({command});
  view.selected_ = 0;
  view.selection_is_explicit_ = true;
  view.Update({Make(Type::kCommand, "", 80)});
  assert(view.selected_ == 1 && view.selection_is_explicit_);
  view.Update({Make(Type::kCommand, "", 80), command});
  assert(view.selected_ == 2 && view.selection_is_explicit_);
  view.selection_is_explicit_ = false;  // Query edit starts a new selection.
  view.Update({command});
  assert(view.selected_ == 0);
  std::cout << "PASS: navigation without keyword, engine-origin filtering, typed action priority, cap, remote/local deduplication, remote ordering, stable selection, removal, empty results and scope identity\n";
}
'''
with tempfile.TemporaryDirectory(prefix='lune-search-model-') as temporary:
    source = Path(temporary) / 'model.cc'
    binary = Path(temporary) / 'model'
    source.write_text(program)
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-arch', args.arch,
                    str(source), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
