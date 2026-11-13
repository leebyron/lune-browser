// Copyright 2026 The Lune Authors
// You can use, redistribute, and/or modify this source code under
// the terms of the GPL-3.0 license that can be found in the LICENSE file.

#include <algorithm>
#include <cmath>
#include <iostream>
#include <string>
#include <string_view>
#include <utility>

#include "base/command_line.h"
#include "base/i18n/break_iterator.h"
#include "base/i18n/char_iterator.h"
#include "base/i18n/icu_util.h"
#include "base/strings/string_util.h"
#include "third_party/icu/source/common/unicode/uchar.h"
#include "third_party/skia/include/core/SkCanvas.h"
#include "ui/gfx/canvas.h"
#include "ui/gfx/font_list.h"
#include "ui/gfx/image/image_skia_rep.h"
#include "ui/gfx/image/image_skia_source.h"

// PRODUCTION_HELPERS

int CheckNames() {
  struct Case {
    const char* name;
    std::u16string_view title;
    size_t length;
  };
  const Case cases[] = {
      {"simple", u"📚 Reading", 2},
      {"flag", u"🇯🇵 Travel", 4},
      {"skin tone", u"👍🏽 Work", 4},
      {"joined", u"👩🏽‍💻 Work", 7},
      {"family", u"👨‍👩‍👧‍👦 Family", 11},
      {"keycap", u"1️⃣ List", 3},
      {"heart variation", u"❤️ Favorites", 2},
      {"bare heart", u"❤ Favorites", 1},
      {"only emoji", u"🌱", 2},
      {"two adjacent emoji", u"📚🚀 Reading", 0},
      {"two spaced emoji", u"📚 🚀 Reading", 0},
      {"later emoji", u"📚 Reading 🚀", 0},
      {"repeated emoji", u"📚📚", 0},
      {"joined plus emoji", u"👩🏽‍💻 Work 📚", 0},
      {"plain", u"Reading", 0},
      {"digit", u"1 Research", 0},
      {"hash", u"# Research", 0},
      {"asterisk", u"* Research", 0},
      {"text presentation", u"❤︎ Reading", 0},
      {"leading whitespace", u" 📚 Reading", 0},
      {"empty", u"", 0},
  };
  for (const auto& item : cases) {
    if (LeadingEmojiLength(item.title) != item.length) {
      std::cerr << item.name << " failed\n";
      return 1;
    }
  }
  const auto title = std::u16string_view(u"📚 \t Reading \u00a0");
  if (base::TrimWhitespace(title.substr(LeadingEmojiLength(title)),
                           base::TRIM_ALL) != u"Reading") {
    return 3;
  }
  std::cout << "PASS 21 Unicode prefix cases and Unicode whitespace trimming\n";
  return 0;
}

int CheckRendering() {
  if (kEmojiFontSize != 16) {
    return 7;
  }
  const gfx::FontList font("Arial, 12px");
  for (const auto& text : {u"📚", u"🇯🇵", u"👩🏽‍💻", u"❤️", u"🌱"}) {
    for (float scale : {1.0f, 2.0f}) {
      TabGroupEmojiImageSource source(text, font, SK_ColorBLACK);
      const auto rep = source.GetImageForScale(scale);
      const auto& bitmap = rep.GetBitmap();
      const auto alpha_rep = TabGroupEmojiImageSource(
          text, font, SkColorSetA(SK_ColorBLACK, 0x55)).GetImageForScale(scale);
      const auto& alpha_bitmap = alpha_rep.GetBitmap();
      bool has_color = false;
      int max_alpha = 0;
      int left = bitmap.width();
      int right = 0;
      int top = bitmap.height();
      int bottom = 0;
      for (int y = 0; y < bitmap.height(); ++y) {
        for (int x = 0; x < bitmap.width(); ++x) {
          const auto color = bitmap.getColor(x, y);
          if (color != alpha_bitmap.getColor(x, y)) {
            return 4;
          }
          max_alpha = std::max(max_alpha, static_cast<int>(SkColorGetA(color)));
          const int chroma =
              std::max({SkColorGetR(color), SkColorGetG(color), SkColorGetB(color)}) -
              std::min({SkColorGetR(color), SkColorGetG(color), SkColorGetB(color)});
          has_color |= SkColorGetA(color) > 200 && chroma > 40;
          if (SkColorGetA(color)) {
            left = std::min(left, x);
            right = std::max(right, x + 1);
            top = std::min(top, y);
            bottom = std::max(bottom, y + 1);
          }
        }
      }
      if (max_alpha != 255 || !has_color) {
        return 5;
      }
      if (right <= left || bottom <= top ||
          std::abs(left + right - bitmap.width()) > 1 ||
          std::abs(top + bottom - bitmap.height()) > 1 ||
          std::max(right - left, bottom - top) < 14 * scale || left == 0 ||
          top == 0 || right == bitmap.width() || bottom == bitmap.height()) {
        std::cerr << "Glyph bounds failed at scale " << scale << ": " << left
                  << "," << top << " to " << right << "," << bottom << "\n";
        return 6;
      }
    }
  }
  std::cout << "PASS 10 production raster size, centering, clipping, full-color "
               "and opacity checks\n";
  return 0;
}

int main(int argc, char** argv) {
  base::CommandLine::Init(argc, argv);
  if (!base::i18n::InitializeICU()) {
    return 2;
  }
  const int names = CheckNames();
  return names ? names : CheckRendering();
}
