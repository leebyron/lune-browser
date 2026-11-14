// Copyright 2026 The Lune Authors
// SPDX-License-Identifier: GPL-3.0-or-later
#include <cstdlib>
#include <ctime>
#include "base/check.h"
#include <iostream>
#include <string>
#include "base/command_line.h"
#include "base/i18n/icu_util.h"
#include "base/i18n/time_formatting.h"
#include "base/strings/utf_string_conversions.h"
#include "base/time/time.h"
#include "third_party/icu/source/i18n/unicode/smpdtfmt.h"
#include "third_party/icu/source/i18n/unicode/timezone.h"

// Keep failures visible even with production logging disabled.
#undef CHECK
#define CHECK(condition) if (condition) {} else Failure(__LINE__)
struct Failure {
  explicit Failure(int line) { std::cerr << "Failed check at fixture line " << line << ": "; }
  template <typename T> Failure& operator<<(const T& value) { std::cerr << value; return *this; }
  ~Failure() { std::cerr << "\n"; std::exit(1); }
};

// Isolate resource lookup; date math and formatting use production base/ICU.
constexpr int IDS_OLDER_TABS_TODAY = 1;
constexpr int IDS_OLDER_TABS_YESTERDAY = 2;
namespace l10n_util {
std::u16string GetStringUTF16(int id) {
  return id == IDS_OLDER_TABS_TODAY ? u"Today" : u"Yesterday";
}
}
class OlderTabsController {
 public:
  static int DateKey(base::Time);
  static std::u16string ShortDate(base::Time, base::Time);
};
// PRODUCTION_HELPERS

base::Time Local(int y, int m, int d, int h = 12, int minute = 0) {
  base::Time::Exploded parts = {y, m, 0, d, h, minute, 0, 0};
  base::Time time;
  CHECK(base::Time::FromLocalExploded(parts, &time));
  return time;
}
int main(int argc, const char** argv) {
  base::CommandLine::Init(argc, argv);
  CHECK(base::i18n::InitializeICU());
  UErrorCode error = U_ZERO_ERROR;
  icu::Locale::setDefault(icu::Locale("en_US"), error);
  CHECK(U_SUCCESS(error));
  setenv("TZ", "America/Los_Angeles", 1);
  tzset();
  icu::TimeZone::adoptDefault(icu::TimeZone::createTimeZone("America/Los_Angeles"));
  const auto now = Local(2026, 11, 14);
  struct Case { int day; const char16_t* expected; };
  for (const auto& c : {Case{14,u"Today"}, {13,u"Yesterday"},
                       {12,u"Thursday"}, {11,u"Wednesday"}, {10,u"Tuesday"},
                       {9,u"Nov 9th"}, {7,u"Nov 7th"}, {6,u"Nov 6th"},
                       {3,u"Nov 3rd"}, {2,u"Nov 2nd"}, {1,u"Nov 1st"}}) {
    auto actual = OlderTabsController::ShortDate(Local(2026,11,c.day),now);
    CHECK(actual == c.expected) << c.day << ": " << base::UTF16ToUTF8(actual);
  }
  for (int d : {11,12,13,21,22,23,31}) {
    auto actual = OlderTabsController::ShortDate(Local(2026,10,d),now);
    const auto suffix = d == 21 || d == 31 ? u"st" : d == 22 ? u"nd" : d == 23 ? u"rd" : u"th";
    CHECK(actual.ends_with(suffix));
  }
  CHECK(OlderTabsController::ShortDate(Local(2025,12,31),Local(2026,1,1)) == u"Yesterday");
  CHECK(OlderTabsController::ShortDate(Local(2024,2,29),Local(2024,3,1)) == u"Yesterday");
  CHECK(OlderTabsController::DateKey(Local(2026,3,9,0)) -
        OlderTabsController::DateKey(Local(2026,3,8,0)) == 1);
  CHECK(OlderTabsController::DateKey(Local(2026,11,2,0)) -
        OlderTabsController::DateKey(Local(2026,11,1,0)) == 1);
  CHECK(OlderTabsController::DateKey(Local(2026,11,14,0)) ==
        OlderTabsController::DateKey(Local(2026,11,14,23,59)));
  CHECK(OlderTabsController::ShortDate(Local(2026,11,13,23,59),Local(2026,11,14,0)) == u"Yesterday");
  CHECK(OlderTabsController::ShortDate(Local(2026,11,9),now) !=
        OlderTabsController::ShortDate(Local(2026,11,8),now));
  CHECK(OlderTabsController::ShortDate(Local(2026,10,1),now) !=
        OlderTabsController::ShortDate(Local(2026,9,1),now));
  std::cout << "PASS: relative dates, separate dates beyond seven days, ordinals, midnight, year, leap day and both DST boundaries\n";
}
