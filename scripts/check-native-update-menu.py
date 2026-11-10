#!/usr/bin/env python3
"""Run the actual app-menu/dispatch and Sparkle state code against native AppKit."""
import argparse
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source',type=Path)
p.add_argument('--arch',choices=['arm64','x86_64'],required=True)
a=p.parse_args();src=a.source.resolve()
def section(name,start,end):
 text=(src/name).read_text();i=text.index(start);return text[i:text.index(end,i)]
menu=section('chrome/browser/ui/cocoa/main_menu_builder.mm','NSMenuItem* BuildAppMenu(', '\nNSMenuItem* BuildFileMenu(')
action=section('chrome/browser/app_controller_mac.mm','- (IBAction)checkForUpdates:', '- (IBAction)orderFrontStandardAboutPanel:')
check=section('chrome/browser/mac/sparkle_glue.mm','void VersionUpdaterSparkle::CheckForUpdate(', '\nvoid VersionUpdaterSparkle::UpdateStatus(')
initialize=section('chrome/browser/mac/sparkle_glue.mm','void InitializeSparkleFramework()', '\nbool SparkleEnabled()')
status=section('chrome/browser/mac/sparkle_glue.mm','- (void)updateStatus:(VersionUpdater::Status)status\n', '\n@end  // @implementation SparkleObserver')
messages={m.attrib['name']:''.join(m.itertext()).strip() for m in ET.parse(src/'chrome/app/generated_resources.grd').iter('message')}
assert messages['IDS_CHECK_FOR_UPDATES_MENU_MAC']=='Check for Updates…'
controller=(src/'chrome/browser/app_controller_mac.mm').read_text()
assert 'action == @selector(checkForUpdates:)' in controller
pages=section('chrome/browser/ui/chrome_pages.cc','void ShowAboutChrome(', '\nvoid ShowHeliumServices(')
assert 'params.navigated_or_inserted_contents' in pages and '!contents->IsLoading()' in pages and 'Reload(content::ReloadType::NORMAL, false)' in pages
names=sorted(set(re.findall(r'\b(?:IDC|IDS)_[A-Z0-9_]+\b',menu)))
ids='enum {'+', '.join(f'{name}={i+1}' for i,name in enumerate(names))+'};\n'
prefix=r'''
#import <AppKit/AppKit.h>
#include <cassert>
#include <functional>
#include <initializer_list>
#include <string>
#define DCHECK_CALLED_ON_VALID_SEQUENCE(x)
struct Profile {};
struct BrowserWindowInterface {};
static BrowserWindowInterface* active_browser;
static int about_checks=0, new_about_windows=0;
BrowserWindowInterface* ActivateBrowser(Profile*) { return active_browser; }
namespace chrome {
void ShowAboutChrome(BrowserWindowInterface*, bool check) { assert(check); ++about_checks; }
void OpenAboutWindow(Profile*) { ++new_about_windows; }
}
namespace base {
std::function<void(Profile*)> BindOnce(void (^block)(Profile*)) {
 return [block](Profile* profile) { block(profile); };
}
}
namespace app_controller_mac {
constexpr int kShowProfilePickerOnFailure=1;
static std::function<void(Profile*)> pending;
void RunInLastProfileSafely(std::function<void(Profile*)> callback, int failure) {
 assert(failure==kShowProfilePickerOnFailure); assert(!pending); pending=callback;
}
void Complete(Profile* profile) { auto cb=std::move(pending); pending={}; cb(profile); }
}
@interface AppController : NSObject
@property(nonatomic) BOOL allowBrowser;
- (BOOL)canOpenNewBrowser;
- (IBAction)checkForUpdates:(id)sender;
- (IBAction)orderFrontStandardAboutPanel:(id)sender;
- (IBAction)showPreferences:(id)sender;
- (IBAction)toggleConfirmToQuit:(id)sender;
@end
@implementation AppController
- (BOOL)canOpenNewBrowser { return self.allowBrowser; }
- (IBAction)orderFrontStandardAboutPanel:(id)sender {}
- (IBAction)showPreferences:(id)sender {}
- (IBAction)toggleConfirmToQuit:(id)sender {}
'''
builder=r'''
NSString* MenuTitle(int id) {
 if (id==IDS_CHECK_FOR_UPDATES_MENU_MAC) return @"Check for Updates…";
 if (id==IDS_IMPORT_SETTINGS_MENU_MAC) return @"Import Bookmarks and Settings…";
 return [NSString stringWithFormat:@"Menu %d",id];
}
struct Item {
 NSMenuItem* native;
 bool removed=false;
 Item(int id=0):native([[NSMenuItem alloc] initWithTitle:MenuTitle(id) action:nil keyEquivalent:@""]) {}
 Item& tag(int n) { native.tag=n; return *this; }
 Item& target(id target) { native.target=target; return *this; }
 Item& action(SEL action) { native.action=action; return *this; }
 Item& command_id(int n) { native.tag=n; return *this; }
 Item& remove_if(bool condition) { removed=condition; return *this; }
 Item& is_separator() { native=[NSMenuItem separatorItem]; return *this; }
 Item& string_format_1(const std::u16string&) { return *this; }
 Item& key_equivalent(NSString* value, NSEventModifierFlags flags) {
  native.keyEquivalent=value; native.keyEquivalentModifierMask=flags; return *this;
 }
 Item& submenu(std::initializer_list<Item> items) {
  NSMenu* m=[[NSMenu alloc] initWithTitle:@""];
  for (const auto& i:items) if (!i.removed) [m addItem:i.native];
  native.submenu=m; return *this;
 }
 NSMenuItem* Build() { return native; }
};
'''
updater=r'''
struct VersionUpdater {
 enum Status { CHECKING, UPDATING, NEARLY_UPDATED, UPDATED, FAILED, DISABLED };
 struct StatusCallback {
  std::function<void(Status,int)> callback;
  void Run(Status s,int p,bool,bool,std::string,int,std::u16string) const { callback(s,p); }
 };
 using PromoteCallback=std::function<void()>;
};
struct StatusList {
 int notifications=0;
 void Notify(VersionUpdater::Status,int,NSString*) { ++notifications; }
};
@interface SparkleObserver : NSObject { @public StatusList status_callbacks_; }
@property(nonatomic) BOOL permitted;
@property(nonatomic,copy) void (^invocationBlock)(void);
@property(nonatomic,strong) NSString* currentlyDownloadedVersion;
@property(nonatomic) VersionUpdater::Status lastStatus;
@property(nonatomic) int lastProgress;
@property(nonatomic,copy) NSString* lastError;
- (BOOL)shouldAccessUpdateService;
- (void)updateStatus:(VersionUpdater::Status)s error_string:(NSString*)error;
- (void)updateProgress:(int)progress;
@end
@implementation SparkleObserver
- (BOOL)shouldAccessUpdateService { return self.permitted; }
'''
updater2=r'''
@interface SPUUpdater : NSObject
@property(nonatomic) BOOL canCheckForUpdates;
@property(nonatomic) BOOL automaticallyChecksForUpdates;
@property(nonatomic) BOOL automaticallyDownloadsUpdates;
@property(nonatomic) BOOL startResult;
@property(nonatomic) int starts;
@property(nonatomic) int checks;
- (BOOL)startUpdater:(NSError**)error;
- (void)checkForUpdatesInBackground;
@end
@implementation SPUUpdater
- (BOOL)startUpdater:(NSError**)error {
 ++_starts;
 if (!_startResult) *error=[NSError errorWithDomain:@"fixture" code:1
  userInfo:@{NSLocalizedDescriptionKey:@"fixture startup failure"}];
 return _startResult;
}
- (void)checkForUpdatesInBackground { ++_checks; _canCheckForUpdates=NO; }
@end
struct VersionUpdaterSparkle : VersionUpdater {
 static SPUUpdater* sparkle_updater_;
 static SparkleObserver* sparkle_observer_;
 StatusCallback status_callback_;
 PromoteCallback promote_callback_;
 void CheckForUpdate(StatusCallback,PromoteCallback);
 void UpdateStatus(Status s,int p,NSString*) { status_callback_.Run(s,p,false,false,"",0,u""); }
};
SPUUpdater* VersionUpdaterSparkle::sparkle_updater_=nil;
SparkleObserver* VersionUpdaterSparkle::sparkle_observer_=nil;
'''
tests=r'''
int main() { @autoreleasepool {
 [NSApplication sharedApplication];
 AppController* controller=[AppController new]; controller.allowBrowser=YES;
 NSMenuItem* app=BuildAppMenu(NSApp,controller,u"Lune",false,false);
 auto* m=app.submenu;
 NSInteger i=[m indexOfItemWithTag:IDC_IMPORT_SETTINGS]; assert(i>=0);
 NSMenuItem* update=[m itemAtIndex:i+1];
 assert([update.title isEqual:@"Check for Updates…"]);
 assert(update.target==controller && update.action==@selector(checkForUpdates:));
 assert(update.keyEquivalent.length==0 && [m itemAtIndex:i+2].separatorItem);
 int count=0; for (NSMenuItem* item in m.itemArray) if(item.action==@selector(checkForUpdates:)) ++count;
 assert(count==1);
 NSMenuItem* pwa=BuildAppMenu(NSApp,controller,u"Lune",true,false);
 for(NSMenuItem* item in pwa.submenu.itemArray) assert(item.action!=@selector(checkForUpdates:));
 puts("PASS: localized app-menu order, separator, target, no shortcut, no PWA entry");
 Profile profile; BrowserWindowInterface browser;
 active_browser=&browser;
 [controller checkForUpdates:update]; assert(app_controller_mac::pending && about_checks==0);
 app_controller_mac::Complete(&profile); assert(about_checks==1 && new_about_windows==0);
 active_browser=nullptr;
 [controller checkForUpdates:update]; app_controller_mac::Complete(&profile);
 assert(new_about_windows==1);
 [controller checkForUpdates:update]; app_controller_mac::Complete(nullptr);
 assert(new_about_windows==1);
 [controller checkForUpdates:update]; controller.allowBrowser=NO;
 app_controller_mac::Complete(&profile); assert(new_about_windows==1);
 [controller checkForUpdates:update]; assert(!app_controller_mac::pending);
 puts("PASS: asynchronous profile loading, no windows, profile failure and shutdown");
 auto* observer=[SparkleObserver new]; auto* updater=[SPUUpdater new];
 VersionUpdaterSparkle::sparkle_observer_=observer; VersionUpdaterSparkle::sparkle_updater_=updater;
 helium::InitializeSparkleFramework(); assert(updater.starts==0);
 observer.permitted=YES; updater.startResult=NO;
 helium::InitializeSparkleFramework(); assert(updater.starts==1 && observer.lastStatus==VersionUpdater::FAILED);
 updater.startResult=YES; updater.canCheckForUpdates=YES;
 helium::InitializeSparkleFramework(); assert(updater.starts==2 && updater.checks==1);
 helium::InitializeSparkleFramework(); assert(updater.starts==2 && updater.checks==1);
 VersionUpdaterSparkle client; VersionUpdater::Status result=VersionUpdater::DISABLED; int progress=-1;
 VersionUpdater::StatusCallback cb{[&](VersionUpdater::Status s,int p){result=s;progress=p;}};
 [observer updateProgress:67]; client.CheckForUpdate(cb,{});
 assert(result==VersionUpdater::UPDATING && progress==67 && updater.checks==1);
 observer.invocationBlock=^{}; client.CheckForUpdate(cb,{});
 assert(result==VersionUpdater::NEARLY_UPDATED && updater.checks==1);
 observer.invocationBlock=nil; observer.currentlyDownloadedVersion=@"next"; client.CheckForUpdate(cb,{});
 assert(result==VersionUpdater::NEARLY_UPDATED && updater.checks==1);
 observer.currentlyDownloadedVersion=nil; observer.permitted=NO; client.CheckForUpdate(cb,{});
 assert(result==VersionUpdater::DISABLED && updater.checks==1 && !observer.permitted);
 observer.permitted=YES; updater.canCheckForUpdates=YES; client.CheckForUpdate(cb,{});
 assert(observer.lastStatus==VersionUpdater::CHECKING && updater.checks==2);
 client.CheckForUpdate(cb,{}); assert(result==VersionUpdater::CHECKING && updater.checks==2);
 [observer updateStatus:VersionUpdater::UPDATED error_string:nil]; updater.canCheckForUpdates=YES;
 client.CheckForUpdate(cb,{}); assert(updater.checks==3);
 puts("PASS: shared updater startup, retry, repeat checks, progress replay, ready state and consent");
}}
'''
program=prefix+action+'\n@end\n'+ids+builder+menu+updater+status+'\n@end\n'+updater2+check+'\nnamespace helium {\n'+initialize+'\n}\n'+tests
with tempfile.TemporaryDirectory(prefix='lune-update-menu-') as tmp:
 path=Path(tmp)/'test.mm';path.write_text(program);exe=Path(tmp)/'test'
 subprocess.run(['xcrun','clang++','-std=c++20','-fobjc-arc','-arch',a.arch,
  '-mmacosx-version-min=13.0','-framework','AppKit','-Wno-deprecated-declarations',str(path),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
