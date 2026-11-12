// Copyright 2026 The Lune Authors
// You can use, redistribute, and/or modify this source code under
// the terms of the GPL-3.0 license that can be found in the LICENSE file.

#import <AppKit/AppKit.h>

#include <cstdio>
#include <cstdlib>

#include "base/i18n/icu_util.h"
#include "chrome/browser/ui/helium/native_word_navigation_mac.h"

static int checks = 0;
static void Expect(NSTextView* editor, NSUInteger start, NSUInteger length,
                   const char* label) {
  ++checks;
  if (!NSEqualRanges(editor.selectedRange, NSMakeRange(start, length))) {
    fprintf(stderr, "FAIL %s: expected %lu,%lu got %lu,%lu affinity=%lu\n",
            label, start, length, editor.selectedRange.location,
            editor.selectedRange.length, editor.selectionAffinity);
    std::abort();
  }
}

@interface WordDelegate : NSObject <NSTextFieldDelegate>
@property NSInteger handled;
@end
@implementation WordDelegate
@synthesize handled = _handled;
- (BOOL)control:(NSControl*)control textView:(NSTextView*)editor
    doCommandBySelector:(SEL)command {
  if (helium::HandleNativeWordNavigation(control, editor, command)) {
    ++self.handled;
    return YES;
  }
  return NO;
}
@end

static void Reset(NSTextField* field, NSString* text, NSUInteger cursor) {
  [field.window makeFirstResponder:nil];
  field.stringValue = text;
  [field selectText:nil];
  field.currentEditor.selectedRange = NSMakeRange(cursor, 0);
}
static void Word(NSTextView* editor, SEL command) {
  [editor doCommandBySelector:command];
}

int main() {
  @autoreleasepool {
    [NSApplication sharedApplication];
    if (!base::i18n::InitializeICU()) return 2;
    NSWindow* window = [[NSWindow alloc]
        initWithContentRect:NSMakeRect(0, 0, 800, 80)
        styleMask:NSWindowStyleMaskTitled
        backing:NSBackingStoreBuffered defer:NO];
    WordDelegate* delegate = [WordDelegate new];
    NSTextField* field = [[NSTextField alloc]
        initWithFrame:NSMakeRect(0, 0, 750, 30)];
    field.usesSingleLineMode = YES;
    field.cell = [[HeliumWordTextFieldCell alloc] initTextCell:@""];
    field.delegate = delegate;
    [window.contentView addSubview:field];

    for (NSString* separator in @[@".", @"-", @"/", @"\uFF0E"]) {
      NSString* text = [NSString stringWithFormat:@"foo%@bar", separator];
      Reset(field, text, 7);
      NSTextView* editor = (NSTextView*)field.currentEditor;
      Word(editor, @selector(moveWordLeft:));
      Expect(editor, 4, 0, "component left");
      Word(editor, @selector(moveWordLeft:));
      Expect(editor, 0, 0, "component left again");
      Word(editor, @selector(moveWordRight:));
      Expect(editor, 3, 0, "component right");
      Word(editor, @selector(moveWordRight:));
      Expect(editor, 7, 0, "component right again");
    }

    Reset(field, @"foo.bar", 7);
    NSTextView* editor = (NSTextView*)field.currentEditor;
    Word(editor, @selector(moveWordLeftAndModifySelection:));
    Expect(editor, 4, 3, "shift left");
    [editor moveRightAndModifySelection:nil];
    Expect(editor, 5, 2, "character shift preserves backwards anchor");
    Word(editor, @selector(moveWordLeftAndModifySelection:));
    Expect(editor, 4, 3, "word after character shift");
    Word(editor, @selector(moveWordLeftAndModifySelection:));
    Expect(editor, 0, 7, "shift all backwards");
    Word(editor, @selector(moveWordRightAndModifySelection:));
    Expect(editor, 3, 4, "reverse shrinks from active end");
    Word(editor, @selector(moveWordRightAndModifySelection:));
    Expect(editor, 7, 0, "reverse collapses at original anchor");

    Reset(field, @"foo.bar-baz", 4);
    editor = (NSTextView*)field.currentEditor;
    Word(editor, @selector(moveWordLeftAndModifySelection:));
    Expect(editor, 0, 4, "backward to before anchor");
    Word(editor, @selector(moveWordRightAndModifySelection:));
    Expect(editor, 3, 1, "shrink to dot");
    Word(editor, @selector(moveWordRightAndModifySelection:));
    Expect(editor, 4, 0, "native word selection collapses at anchor");
    Word(editor, @selector(moveWordRightAndModifySelection:));
    Expect(editor, 4, 3, "extend beyond original anchor");
    [editor moveLeftAndModifySelection:nil];
    Expect(editor, 4, 2, "character shift preserves forward anchor");
    Word(editor, @selector(moveWordRightAndModifySelection:));
    Expect(editor, 4, 3, "word after forward character shrink");

    for (NSArray* pair in @[
             @[@"3.14", @4], @[@"foo_bar", @7], @[@"e\u0301.bar", @2],
             @[@"\U0001F469\u200D\U0001F4BBfoo.bar", @8]]) {
      NSString* text = pair[0];
      Reset(field, text, 0);
      editor = (NSTextView*)field.currentEditor;
      Word(editor, @selector(moveWordRight:));
      Expect(editor, [pair[1] unsignedIntegerValue], 0,
             "decimal, underscore and Unicode boundaries");
    }
    Reset(field, @"https://example.com/path-name", 29);
    editor = (NSTextView*)field.currentEditor;
    for (NSNumber* stop in @[@25, @20, @16, @8, @0]) {
      Word(editor, @selector(moveWordLeft:));
      Expect(editor, stop.unsignedIntegerValue, 0, "URL traversal");
    }

    for (NSArray* pair in @[
             @[@"moveWordForward:", @3, @0],
             @[@"moveWordForwardAndModifySelection:", @0, @3]]) {
      Reset(field, @"foo.bar", 0);
      editor = (NSTextView*)field.currentEditor;
      Word(editor, NSSelectorFromString(pair[0]));
      Expect(editor, [pair[1] unsignedIntegerValue],
             [pair[2] unsignedIntegerValue], "logical forward");
    }
    for (NSArray* pair in @[
             @[@"moveWordBackward:", @4, @0],
             @[@"moveWordBackwardAndModifySelection:", @4, @3]]) {
      Reset(field, @"foo.bar", 7);
      editor = (NSTextView*)field.currentEditor;
      Word(editor, NSSelectorFromString(pair[0]));
      Expect(editor, [pair[1] unsignedIntegerValue],
             [pair[2] unsignedIntegerValue], "logical backward");
    }

    // Native hyphen navigation is an independent oracle for bidi traversal
    // and selection anchoring; dotted components should have the same stops.
    for (NSArray* pair in @[
             @[@"אבג.דהו", @"אבג-דהו"],
             @[@"abc.אבג xyz.דהו", @"abc-אבג xyz-דהו"]]) {
      for (NSString* action in @[@"moveWordLeft:", @"moveWordRight:",
               @"moveWordLeftAndModifySelection:",
               @"moveWordRightAndModifySelection:"]) {
        BOOL left = [action containsString:@"Left"];
        SEL command = NSSelectorFromString(action);
        Reset(field, pair[0], left ? [pair[0] length] : 0);
        editor = (NSTextView*)field.currentEditor;
        NSTextView* reference = [[NSTextView alloc]
            initWithFrame:NSMakeRect(0, 0, 750, 30)];
        reference.string = pair[1];
        reference.selectedRange = NSMakeRange(left ? [pair[1] length] : 0, 0);
        for (int i = 0; i < 8; ++i) {
          Word(editor, command);
          [reference doCommandBySelector:command];
          if (!NSEqualRanges(editor.selectedRange, reference.selectedRange)) {
            fprintf(stderr, "bidi text=%s action=%s iteration=%d reference affinity=%lu\n",
                    [pair[0] UTF8String], action.UTF8String, i,
                    reference.selectionAffinity);
          }
          Expect(editor, reference.selectedRange.location,
                 reference.selectedRange.length, "bidi native-hyphen parity");
        }
      }
    }

    Reset(field, @"foo.bar", 7);
    editor = (NSTextView*)field.currentEditor;
    for (NSNumber* shift in @[@NO, @YES]) {
      Reset(field, @"foo.bar", 7);
      editor = (NSTextView*)field.currentEditor;
      NSEventModifierFlags flags = NSEventModifierFlagOption |
          NSEventModifierFlagFunction | NSEventModifierFlagNumericPad;
      if (shift.boolValue) flags |= NSEventModifierFlagShift;
      NSEvent* event = [NSEvent keyEventWithType:NSEventTypeKeyDown
          location:NSZeroPoint modifierFlags:flags timestamp:0
          windowNumber:window.windowNumber context:nil
          characters:@"\uF702" charactersIgnoringModifiers:@"\uF702"
          isARepeat:NO keyCode:123];
      [editor keyDown:event];
      Expect(editor, 4, shift.boolValue ? 3 : 0, "Option key event");
    }

    Reset(field, @"foo.bar", 0);
    editor = (NSTextView*)field.currentEditor;
    ++checks;
    if (helium::HandleNativeWordNavigation(field, editor, @selector(insertTab:)))
      std::abort();
    Expect(editor, 0, 0, "unrelated command preparation preserves selection");
    [editor setMarkedText:@"composing" selectedRange:NSMakeRange(0, 0)
         replacementRange:NSMakeRange(0, 0)];
    ++checks;
    const NSRange markedSelection = editor.selectedRange;
    if (helium::HandleNativeWordNavigation(field, editor, @selector(moveWordRight:)))
      std::abort();
    if (!editor.hasMarkedText || !NSEqualRanges(editor.selectedRange, markedSelection))
      std::abort();
    [editor unmarkText];

    Reset(field, @"foo.bar", 7);
    editor = (NSTextView*)field.currentEditor;
    Word(editor, @selector(moveWordLeft:));
    editor.selectedRange = NSMakeRange(7, 0);
    Word(editor, @selector(deleteWordBackward:));
    ++checks;
    if (editor.string.length != 0) {
      fprintf(stderr, "FAIL native deletion: %s\n", editor.string.UTF8String);
      std::abort();
    }

    // The same window-owned editor must keep native boundaries in an unrelated
    // control that does not opt in to the word-navigation adapter.
    NSTextField* other = [[NSTextField alloc]
        initWithFrame:NSMakeRect(0, 35, 750, 30)];
    [window makeFirstResponder:nil];
    [window.contentView addSubview:other];
    other.stringValue = @"foo.bar";
    [other selectText:nil];
    NSTextView* otherEditor = (NSTextView*)other.currentEditor;
    otherEditor.selectedRange = NSMakeRange(7, 0);
    [otherEditor moveWordLeft:nil];
    Expect(otherEditor, 0, 0, "shared editor does not change unrelated controls");

    // First-time TextKit compatibility/storage setup must retain a selection
    // anchor created by ordinary native character selection before opting in.
    NSWindow* freshWindow = [[NSWindow alloc]
        initWithContentRect:NSMakeRect(0, 0, 800, 80)
        styleMask:NSWindowStyleMaskTitled
        backing:NSBackingStoreBuffered defer:NO];
    NSTextField* fresh = [[NSTextField alloc]
        initWithFrame:NSMakeRect(0, 0, 750, 30)];
    fresh.cell = [[HeliumWordTextFieldCell alloc] initTextCell:@""];
    fresh.delegate = delegate;
    [freshWindow.contentView addSubview:fresh];
    Reset(fresh, @"foo.bar", 7);
    NSTextView* freshEditor = (NSTextView*)fresh.currentEditor;
    [freshEditor moveLeftAndModifySelection:nil];
    Word(freshEditor, @selector(moveWordLeftAndModifySelection:));
    Expect(freshEditor, 4, 3, "first-time setup keeps native selection anchor");

    NSWindow* undoWindow = [[NSWindow alloc]
        initWithContentRect:NSMakeRect(0, 0, 800, 80)
        styleMask:NSWindowStyleMaskTitled
        backing:NSBackingStoreBuffered defer:NO];
    NSTextField* undoField = [[NSTextField alloc]
        initWithFrame:NSMakeRect(0, 0, 750, 30)];
    undoField.cell = [[HeliumWordTextFieldCell alloc] initTextCell:@""];
    undoField.delegate = delegate;
    [undoWindow.contentView addSubview:undoField];
    Reset(undoField, @"foo.bar", 7);
    NSTextView* undoEditor = (NSTextView*)undoField.currentEditor;
    undoEditor.allowsUndo = YES;
    [undoEditor.undoManager removeAllActions];
    [undoEditor.undoManager beginUndoGrouping];
    [undoEditor insertText:@"!" replacementRange:NSMakeRange(NSNotFound, 0)];
    [undoEditor.undoManager endUndoGrouping];
    Word(undoEditor, @selector(moveWordLeft:));
    Expect(undoEditor, 4, 0, "word jump after typing before first-time setup");
    ++checks;
    if (!undoEditor.undoManager.canUndo) {
      fprintf(stderr, "FAIL undo history was cleared by first word jump\n");
      std::abort();
    }
    [undoEditor.undoManager undo];
    ++checks;
    if (![undoEditor.string isEqualToString:@"foo.bar"]) {
      fprintf(stderr, "FAIL undo text: %s\n", undoEditor.string.UTF8String);
      std::abort();
    }
    ++checks;
    if (delegate.handled < 30) {
      fprintf(stderr, "FAIL adapter dispatch count: %ld\n", delegate.handled);
      std::abort();
    }
    printf("PASS %d native word movement/selection checks with production ICU\n",
           checks);
  }
}
