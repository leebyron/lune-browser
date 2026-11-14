#!/usr/bin/env python3
"""Exercise production address-bar scope layout and key handling with AppKit.

Engine/browser doubles isolate scope transitions. Real catalogue ranking is
covered by check-command-bangs.py; word movement by check-native-word-navigation.py.
Navigation needs a browser fixture.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--arch', required=True, choices=('arm64', 'x86_64'))
args = parser.parse_args()
source = (args.source / 'chrome/browser/ui/views/frame/browser_frame_view_mac.mm').read_text()
frame_start = source.index('static NSRect HeliumAddressEditingFrame(')
editing_frame = source[frame_start:source.index('\n}', frame_start) + 2]
source = source[source.index('@implementation HeliumFloatingAddressBar'):]


def method(signature):
    start = source.index(signature)
    end = source.find('\n- (', start + len(signature))
    return source[start:end]


pill = (args.source / 'chrome/browser/ui/helium/native_result_row_mac.mm').read_text()
pill = pill[pill.index('@implementation HeliumNativeScopePill'):]
pill = pill[:pill.index('\n@end') + len('\n@end')]
program = r'''
#import <AppKit/AppKit.h>
#include <algorithm>
#include <cassert>
#include <memory>
#include <optional>
#include <string>
#include <vector>
''' + editing_frame + r'''
// This fixture sends scope commands only. The production word adapter is
// exercised with real Chromium ICU by check-native-word-navigation.py.
namespace helium {
bool HandleNativeWordNavigation(NSControl*, NSTextView*, SEL) { return false; }
}
namespace base {
NSString* SysUTF16ToNSString(const std::u16string& s) {
  return [[NSString alloc] initWithCharacters:(const unichar*)s.data() length:s.size()];
}
std::u16string SysNSStringToUTF16(NSString* s) {
  std::u16string result(s.length, 0);
  [s getCharacters:(unichar*)result.data() range:NSMakeRange(0, s.length)];
  return result;
}
std::u16string UTF8ToUTF16(const std::string& s) { return {s.begin(), s.end()}; }
}
constexpr int IDS_ACCNAME_LOCATION = 1;
namespace l10n_util { std::u16string GetStringUTF16(int) { return u"Address"; } }
struct Profile {};
struct BrowserView {
  BrowserView* browser() { return this; }
  Profile profile;
  int focused = 0;
  Profile* GetProfile() { return &profile; }
  BrowserView* GetActiveWebContents() { return this; }
  void Focus() { ++focused; }
};
struct TemplateURLService {};
struct TemplateURLServiceFactory {
  static TemplateURLService* GetForProfile(Profile*) { return nullptr; }
};
struct LocationBarModel {
  static LocationBarModel* From(BrowserView*) { static LocationBarModel model; return &model; }
  int GetURL() { return 1; }
};
struct ChromeAutocompleteSchemeClassifier {
  explicit ChromeAutocompleteSchemeClassifier(Profile*) {}
};
namespace metrics { struct OmniboxEventProto { static constexpr int OTHER = 0; }; }
struct AutocompleteInput {
  std::u16string value;
  AutocompleteInput(std::u16string text, int, ChromeAutocompleteSchemeClassifier) : value(text) {}
  void set_current_url(int) {}
  void set_prevent_inline_autocomplete(bool) {}
  void set_in_keyword_mode(bool) {}
  const std::u16string& text() const { return value; }
  static void* GetSubstitutingTemplateURLForInput(TemplateURLService*, AutocompleteInput*) { return nullptr; }
};
namespace helium_command_bar_model {
struct KeywordSplit { std::string keyword; bool has_remainder; };
std::optional<KeywordSplit> SplitKeyword(const std::u16string& q, bool) {
  auto space = q.find(u' ');
  if (space == q.npos) return std::nullopt;
  return KeywordSplit{std::string(q.begin(), q.begin()+space),
                     q.find_first_not_of(u' ', space) != q.npos};
}
bool EngineOwnsKeyword(TemplateURLService*, const std::string& s) {
  return s == "!w" || s == "!gh";
}
std::u16string SiteScopeName(TemplateURLService*, const std::string& s) {
  return s == "!w" ? u"Wikipedia" : u"GitHub";
}
}
enum class AutocompleteStopReason { kInteraction, kClobbered };
struct AutocompleteController {
  int starts = 0, stops = 0;
  void Stop(AutocompleteStopReason) { ++stops; }
  void Start(const AutocompleteInput&) { ++starts; }
};
struct HeliumAddressResult { std::optional<int> bang; };
@interface HeliumNativeScopePill : NSBox
@property(nonatomic, readonly) NSTextField* label;
@end
''' + pill + r'''
@interface Address : NSView {
 @public
  BrowserView* _browserView;
  NSTextField* _address;
  NSView* _addressContainer;
  HeliumNativeScopePill* _scopePill;
  std::string _scopeKeyword;
  BOOL _scopeWasTyped;
  NSInteger _selected;
  BOOL _selectionIsExplicit;
  std::vector<HeliumAddressResult> _results;
  std::unique_ptr<AutocompleteController> _autocomplete;
  int _updates, _accepted, _finished;
}
- (void)layoutScope;
- (void)enterBang:(const std::string&)keyword query:(const std::u16string&)query typed:(BOOL)typed;
- (void)leaveBangRestoringTrigger:(BOOL)restore;
- (void)controlTextDidChange:(NSNotification*)notification;
- (void)acceptAddress;
- (void)finishEditing;
- (void)updateSuggestions;
@end
@implementation Address
- (void)acceptAddress { ++_accepted; }
- (void)finishEditing { ++_finished; }
- (void)updateSuggestions { ++_updates; }
''' + '\n'.join(method(s) for s in [
    '- (void)layoutScope {', '- (void)enterBang:',
    '- (void)leaveBangRestoringTrigger:', '- (void)controlTextDidChange:',
    '- (BOOL)control:(NSControl*)control']) + r'''
@end
int main() {
 @autoreleasepool {
  [NSApplication sharedApplication];
  NSWindow* window = [[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,480,100)
      styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
  Address* owner = [[Address alloc] initWithFrame:window.contentView.bounds];
  window.contentView = owner;
  BrowserView browser;
  owner->_browserView = &browser;
  owner->_autocomplete = std::make_unique<AutocompleteController>();
  owner->_addressContainer = [[NSView alloc] initWithFrame:NSMakeRect(40,8,400,20)];
  [owner addSubview:owner->_addressContainer];
  owner->_address = [[NSTextField alloc] initWithFrame:owner->_addressContainer.bounds];
  [owner->_addressContainer addSubview:owner->_address];
  owner->_scopePill = [[HeliumNativeScopePill alloc] init];
  [owner addSubview:owner->_scopePill];
  [window makeKeyAndOrderFront:nil];
  auto key = [&](SEL command) {
    return [owner control:owner->_address textView:(NSTextView*)owner->_address.currentEditor
        doCommandBySelector:command];
  };
  [owner enterBang:std::string("!w") query:u"Cats and Dogs 🐈" typed:YES];
  assert(owner->_scopeKeyword == "!w" && owner->_scopeWasTyped);
  assert([owner->_scopePill.label.stringValue isEqualToString:@"Wikipedia"]);
  assert([owner->_address.placeholderString isEqualToString:@"Search Wikipedia"]);
  assert(!owner->_scopePill.hidden && NSMinX(owner->_address.frame) > 0);
  assert(owner->_address.currentEditor);
  owner->_address.currentEditor.selectedRange = NSMakeRange(0,0);
  assert(key(@selector(deleteBackward:)));
  assert(owner->_scopeKeyword.empty() && owner->_scopePill.hidden);
  assert([owner->_address.stringValue isEqualToString:@"!w Cats and Dogs 🐈"]);
  assert(owner->_address.currentEditor.selectedRange.location == 2);
  for (auto query : {u"", u"Cats and Dogs 🐈"}) {
    [owner enterBang:std::string("!gh") query:query typed:NO];
    owner->_address.currentEditor.selectedRange = NSMakeRange(0,0);
    assert(key(@selector(deleteBackward:)));
    assert(base::SysNSStringToUTF16(owner->_address.stringValue) == query);
    assert(owner->_address.currentEditor.selectedRange.location == 0);
  }
  [owner enterBang:std::string("!w") query:u"" typed:YES];
  owner->_address.currentEditor.selectedRange = NSMakeRange(0,0);
  assert(key(@selector(deleteBackward:)));
  assert([owner->_address.stringValue isEqualToString:@"!w"]);
  [owner enterBang:std::string("!w") query:u"terms" typed:YES];
  owner->_address.currentEditor.selectedRange = NSMakeRange(0,2);
  assert(!key(@selector(deleteBackward:)));  // Selection deletes normally.
  owner->_address.currentEditor.selectedRange = NSMakeRange(1,0);
  assert(!key(@selector(deleteBackward:)));  // Ordinary query deletion.
  assert(key(@selector(cancelOperation:)));
  assert(owner->_scopeKeyword.empty() && owner->_finished == 0);
  assert([owner->_address.stringValue isEqualToString:@"terms"]);
  assert(key(@selector(cancelOperation:)) && owner->_finished == 1);
  [owner enterBang:std::string("!missing") query:u"lost" typed:NO];
  assert(owner->_scopeKeyword.empty());  // Stale completion cannot enter.
  owner->_results = {{1}};
  assert(key(@selector(insertTab:)) && owner->_accepted == 1);
  assert(key(@selector(insertNewline:)) && owner->_accepted == 2);
  [owner enterBang:std::string("!w") query:u"" typed:YES];
  owner->_addressContainer.frame = NSMakeRect(40,8,100,20);
  [owner layoutScope];
  assert(NSWidth(owner->_scopePill.frame) <= 40);
  assert(NSMaxX(owner->_address.frame) <= 100);
  assert(NSWidth(owner->_address.frame) >= 0);
  // Exact trigger + Space enters scope before starting any suggestions.
  [owner leaveBangRestoringTrigger:NO];
  owner->_address.stringValue = @"!w ";
  int starts = owner->_autocomplete->starts;
  [owner controlTextDidChange:nil];
  assert(owner->_scopeKeyword == "!w" && owner->_scopeWasTyped);
  assert(owner->_address.stringValue.length == 0);
  assert(owner->_autocomplete->starts == starts);
  owner->_address.stringValue = @"private query";
  [owner controlTextDidChange:nil];
  assert(owner->_autocomplete->starts == starts);
  assert(owner->_autocomplete->stops > 0);
  [owner leaveBangRestoringTrigger:NO];
  owner->_address.stringValue = @"!unknown ";
  [owner controlTextDidChange:nil];
  assert(owner->_scopeKeyword.empty());
  assert(owner->_autocomplete->starts == starts + 2);
  assert(owner->_updates >= 10);
  puts("PASS: production native scope entry, retained Unicode terms, provider pill, placeholder, narrow layout, typed/completed Backspace and caret, selection deletion, Escape, stale provider, Tab and Enter dispatch, exact-Space scope, scoped provider cancellation and zero suggestion starts, unknown-trigger fallback");
 }
}
'''
with tempfile.TemporaryDirectory(prefix='lune-address-bangs-') as temporary:
    cpp = Path(temporary) / 'address.mm'
    binary = Path(temporary) / 'address'
    cpp.write_text(program)
    subprocess.run(['/usr/bin/clang++', '-std=c++20', '-fobjc-arc', '-arch', args.arch,
                    '-framework', 'AppKit', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
