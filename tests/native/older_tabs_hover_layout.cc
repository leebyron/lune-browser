// Copyright 2026 The Lune Authors
// SPDX-License-Identifier: GPL-3.0-or-later
#include <iostream>
#include <memory>
#include <cstdlib>

#include "base/at_exit.h"
#include "base/command_line.h"
#include "base/files/file_path.h"
#include "base/i18n/icu_util.h"
#include "chrome/browser/ui/color/chrome_color_id.h"
#include "chrome/browser/ui/layout_constants.h"
#include "chrome/browser/ui/views/tabs/hovercard/fade_label_view.h"
#include "ui/accessibility/platform/ax_platform.h"
#include "ui/base/resource/resource_bundle.h"
#include "ui/base/metadata/metadata_impl_macros.h"
#include "ui/gfx/canvas.h"
#include "third_party/skia/include/core/SkBitmap.h"
#include "ui/views/background.h"
#include "ui/views/border.h"
#include "ui/views/controls/image_view.h"
#include "ui/compositor/layer.h"
#include "ui/views/layout/flex_layout.h"
#include "ui/views/layout/layout_provider.h"
#include "ui/views/view.h"
#include "ui/views/view_class_properties.h"
#include "ui/views/views_delegate.h"

constexpr auto kTextMargins = gfx::Insets::VH(12, 12);
// PRODUCTION_FOOTER_CONSTANTS
// This layout fixture covers the standard macOS interface. Browser builds use
// the actual getter (including its touch-interface variant).
int GetLayoutConstant(LayoutConstant constant) {
  if (constant == LayoutConstant::kTabAlertIndicatorIconWidth) return 16;
  std::abort();
}
class Delegate : public views::ViewsDelegate {};
class AXDelegate : public ui::AXPlatform::Delegate {
 public:
  ui::AXMode GetAccessibilityMode() override { return {}; }
};

// Use the actual FooterRow constructor and footer layout with representative
// memory text. Browser-model state and native SF rasterization are separate.
class MemoryRow : public views::View {
  METADATA_HEADER(MemoryRow, views::View)
 public:
  explicit MemoryRow(bool is_fade_out_view = false) {
    // PRODUCTION_MEMORY_ROW
    icon_->SetImageSize(gfx::Size(16, 16));
    icon_->SetPreferredSize(gfx::Size(16, 16));
    footer_label_->SetText(u"Memory usage: 18.5 MB");
  }
  views::Label* label() { return footer_label_; }
  views::ImageView* icon() { return icon_; }
 private:
  raw_ptr<views::ImageView> icon_ = nullptr;
  raw_ptr<views::Label> footer_label_ = nullptr;
};
BEGIN_METADATA(MemoryRow)
END_METADATA

class FooterLayout : public views::View {
  METADATA_HEADER(FooterLayout, views::View)
 public:
  FooterLayout() {
    // PRODUCTION_EXISTING_LAYOUT
    memory_row_ = AddChildView(std::make_unique<MemoryRow>());
  }
  views::FlexLayout* flex_layout() { return flex_layout_; }
  views::Label* memory_label() { return memory_row_->label(); }
  views::ImageView* memory_icon() { return memory_row_->icon(); }
 private:
  raw_ptr<views::FlexLayout> flex_layout_ = nullptr;
  raw_ptr<MemoryRow> memory_row_ = nullptr;
};

BEGIN_METADATA(FooterLayout)
END_METADATA

class Row : public views::View {
 public:
  Row() {
    SetLayoutManager(std::make_unique<views::FlexLayout>())
        ->SetOrientation(views::LayoutOrientation::kVertical)
        .SetCrossAxisAlignment(views::LayoutAlignment::kStretch)
        .SetCollapseMargins(true);
    footer_view_ = AddChildView(std::make_unique<FooterLayout>());
    // PRODUCTION_FOOTER
  }
  bool CheckAtWidth(int width, const std::u16string& text, bool memory) {
    const bool show_last_used = true;
    footer_view_->SetVisible(memory);
    last_used_label_->SetData({text});
    last_used_label_->SetFade(1);
    last_used_label_->SetVisible(true);
    if (last_used_container_) {
      last_used_container_->SetVisible(true);
      // PRODUCTION_SPACING
    }
    SetSize({width, GetLayoutManager()->GetPreferredHeightForWidth(this, width)});
    DeprecatedLayoutImmediately();
    auto* primary = last_used_label_->GetPrimaryViewForTesting();
    const auto preferred = primary->GetPreferredSize(
        views::SizeBounds(views::SizeBound(primary->width()), views::SizeBound()));
    if (primary->width() <= 0 || primary->height() < preferred.height() ||
        primary->height() < primary->GetLineHeight()) {
      std::cerr << "Clipped text at width " << width << ": "
                << primary->bounds().ToString() << " vs "
                << preferred.ToString() << "\n";
      return false;
    }
    gfx::Rect date_bounds = primary->GetLocalBounds();
    date_bounds = views::View::ConvertRectToTarget(primary, this, date_bounds);
    if (memory) {
      auto* label = footer_view_->memory_label();
      gfx::Rect memory_bounds = label->GetLocalBounds();
      memory_bounds = views::View::ConvertRectToTarget(label, this, memory_bounds);
      const int gap = date_bounds.y() - memory_bounds.bottom();
      if (last_used_icon_) {
        const auto icon = views::View::ConvertRectToTarget(
            last_used_icon_, this, last_used_icon_->GetLocalBounds());
        auto* memory_icon_view = footer_view_->memory_icon();
        const auto memory_icon = views::View::ConvertRectToTarget(
            memory_icon_view, this, memory_icon_view->GetLocalBounds());
        if (icon.size() != memory_icon.size() || icon.x() != memory_icon.x() ||
            date_bounds.x() != memory_bounds.x() ||
            date_bounds.x() - icon.right() != kIconLabelSpacing ||
            icon.y() - date_bounds.y() != memory_icon.y() - memory_bounds.y()) {
          std::cerr << "Date icon/text metrics differ from the memory row\n";
          return false;
        }
      }
      if (gap != kFooterRowSpacing) {
        std::cerr << "Unexpected memory/date gap: " << gap << "\n";
        return false;
      }
    } else if (date_bounds.y() != kTextMargins.top()) {
      std::cerr << "Date-only footer lost its outer top padding\n";
      return false;
    }
    if (height() - date_bounds.bottom() != kTextMargins.bottom()) {
      std::cerr << "Footer lost its outer bottom padding\n";
      return false;
    }
    return true;
  }
 private:
  raw_ptr<FooterLayout> footer_view_ = nullptr;
  raw_ptr<views::View> last_used_container_ = nullptr;
  raw_ptr<FadeLabelView> last_used_label_ = nullptr;
  raw_ptr<views::ImageView> last_used_icon_ = nullptr;
};

bool CheckFadeColors() {
  // An unconfigured fading label reproduces the mismatched mask from the
  // reported transition. Configuring its footer surface must remove that flash.
  FadeLabelView legacy(2, views::style::CONTEXT_DIALOG_BODY_TEXT,
                       views::style::STYLE_BODY_4);
  legacy.SetData({u"Old date"});
  legacy.SetData({u"New date"});
  legacy.SetFade(0);
  gfx::Canvas control(gfx::Size(40, 20), 1, false);
  const SkColor footer = SkColorSetRGB(214, 225, 209);
  control.DrawColor(footer);
  static_cast<FadeLabel*>(legacy.children()[1])->OnPaintBackground(&control);
  if (control.GetBitmap().getColor(1, 1) == footer) {
    std::cerr << "Control did not reproduce the mismatched fade mask\n";
    return false;
  }
  FadeLabelView label(2, views::style::CONTEXT_DIALOG_BODY_TEXT,
                      views::style::STYLE_BODY_4);
  for (SkColor background : {SkColorSetRGB(214, 225, 209),
                             SkColorSetRGB(28, 36, 30)}) {
    for (double percent : {0., .25, .5, .75, 1.}) {
      label.SetData({u"Thursday at 8:23am"});
      label.SetData({u"Nov 9th at 8:23am"});
      label.SetFade(percent);
      label.SetBackgroundColor(background);
      auto* old = static_cast<FadeLabel*>(label.children()[1]);
      const int expected_alpha = static_cast<int>(255 * (1 - percent));
      if (SkColorGetA(old->GetBackgroundColor()) != expected_alpha) {
        std::cerr << "Background update changed the current fade opacity\n";
        return false;
      }
      gfx::Canvas canvas(gfx::Size(40, 20), 1, false);
      canvas.DrawColor(background);
      old->OnPaintBackground(&canvas);
      const SkColor pixel = canvas.GetBitmap().getColor(1, 1);
      // An alpha-composited 8-bit channel can round by one level.
      const auto close = [](int a, int b) { return a - b <= 1 && b - a <= 1; };
      if (!close(SkColorGetR(pixel), SkColorGetR(background)) ||
          !close(SkColorGetG(pixel), SkColorGetG(background)) ||
          !close(SkColorGetB(pixel), SkColorGetB(background))) {
        std::cerr << "Fade mask changed color at " << percent << ": "
                  << std::hex << pixel << " vs " << background << " (mask "
                  << old->GetBackgroundColor() << ")\n";
        return false;
      }
    }
  }
  return true;
}

int main(int argc, char** argv) {
  base::AtExitManager at_exit;
  base::CommandLine::Init(argc, argv);
  if (!base::i18n::InitializeICU()) return 2;
  ui::ResourceBundle::InitSharedInstanceWithPakPath(base::FilePath(argv[1]));
  AXDelegate ax_delegate;
  ui::AXPlatform ax_platform(ax_delegate);
  Delegate delegate;
  views::LayoutProvider layout_provider;
  {
    Row row;
    for (int width : {148, 180, 207, 240}) {
      for (const auto* text : {u"Thursday at 8:23am",
                               u"Nov 9th at 8:23am"}) {
        for (bool memory : {false, true}) {
          if (!row.CheckAtWidth(width, text, memory)) return 1;
        }
      }
    }
    if (!CheckFadeColors()) return 1;
  }
  ui::ResourceBundle::CleanupSharedInstance();
  std::cout << "PASS: visible date text, matching memory icon/text metrics, 8 DIP row gap, outer padding, "
               "and stable light/dark fade-mask pixels at all fade steps\n";
}
