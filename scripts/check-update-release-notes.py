#!/usr/bin/env python3
"""Exercise the production Sparkle downloaded-release capture on native AppKit."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('source', type=Path)
p.add_argument('--arch', choices=['arm64', 'x86_64'], required=True)
a = p.parse_args()
s = a.source.resolve()
text = (s/'chrome/browser/mac/sparkle_glue.mm').read_text()
capture = text[text.index('- (BOOL)updater:(SPUUpdater*)updater\n    shouldPostponeRelaunchForUpdate:'):text.index('// There is a downloaded and unarchived version')]
getters = text[text.index('std::optional<std::string> CurrentlyDownloadedVersion()'):text.index('void SwitchUnderlyingUpdaterProfile(')]
program = r'''
#import <AppKit/AppKit.h>
#include <cassert>
#include <algorithm>
#include <optional>
#include <string>
namespace base {
std::string SysNSStringToUTF8(NSString* s) { return s.UTF8String; }
// Only the version validity dependency is stubbed; capture and URL selection are production code.
struct Version {
 std::string value;
 explicit Version(std::string v) : value(v) {}
 bool IsValid() const { return !value.empty() && std::all_of(value.begin(), value.end(), [](char c) { return (c >= '0' && c <= '9') || c == '.'; }); }
};
}
struct VersionUpdater { enum Status { NEARLY_UPDATED }; };
struct Callbacks { int calls=0; void Notify() { ++calls; } };
Callbacks& UpdateReadyCallbacks() { static Callbacks c; return c; }
@class SPUUpdater;
@interface SUAppcastItem : NSObject
@property(nonatomic,copy) NSString* versionString;
@property(nonatomic,strong) NSURL* releaseNotesURL;
@end
@implementation SUAppcastItem
@end
@interface SparkleObserver : NSObject
@property(nonatomic,copy) NSString* currentlyDownloadedVersion;
@property(nonatomic,copy) NSString* currentlyDownloadedReleaseNotesURL;
@property(nonatomic,copy) void (^invocationBlock)(void);
- (void)updateStatus:(VersionUpdater::Status)status error_string:(NSString*)error;
@end
@implementation SparkleObserver
@synthesize currentlyDownloadedVersion = currentlyDownloadedVersion_;
- (void)updateStatus:(VersionUpdater::Status)status error_string:(NSString*)error {
 assert(status == VersionUpdater::NEARLY_UPDATED);
 assert(self.currentlyDownloadedReleaseNotesURL != nil || self.currentlyDownloadedVersion != nil);
}
'''+capture+r'''
@end
struct VersionUpdaterSparkle { static SparkleObserver* sparkle_observer_; };
SparkleObserver* VersionUpdaterSparkle::sparkle_observer_ = nil;
namespace helium {
'''+getters+r'''
}
int main() { @autoreleasepool {
 assert(!helium::CurrentlyDownloadedReleaseNotesURL());
 assert(!helium::ApplicationIsNearlyUpdated());
 auto* observer = [SparkleObserver new];
 VersionUpdaterSparkle::sparkle_observer_ = observer;
 assert(!helium::CurrentlyDownloadedReleaseNotesURL());
 auto* item = [SUAppcastItem new];
 item.versionString = @"26.1113.1";
 item.releaseNotesURL = [NSURL URLWithString:@"https://github.com/leebyron/lune-browser/releases/tag/v26.1113.1"];
 __block int installs = 0;
 assert([observer updater:nil shouldPostponeRelaunchForUpdate:item untilInvokingBlock:^{ ++installs; }]);
 assert(helium::CurrentlyDownloadedVersion() == "26.1113.1");
 assert(helium::CurrentlyDownloadedReleaseNotesURL() == item.releaseNotesURL.absoluteString.UTF8String);
 assert(helium::ApplicationIsNearlyUpdated() && installs == 0);
 assert(UpdateReadyCallbacks().calls == 1);
 item.versionString = @"26.1114.1";
 item.releaseNotesURL = [NSURL URLWithString:@"https://github.com/leebyron/lune-browser/releases/tag/v26.1114.1"];
 [observer updater:nil shouldPostponeRelaunchForUpdate:item untilInvokingBlock:^{ ++installs; }];
 assert(helium::CurrentlyDownloadedReleaseNotesURL() == item.releaseNotesURL.absoluteString.UTF8String);
 assert(UpdateReadyCallbacks().calls == 2 && installs == 0);
 item.releaseNotesURL = nil;
 [observer updater:nil shouldPostponeRelaunchForUpdate:item untilInvokingBlock:^{ ++installs; }];
 assert(helium::CurrentlyDownloadedReleaseNotesURL() == "https://github.com/leebyron/lune-browser/releases/tag/v26.1114.1");
 assert(helium::ApplicationIsNearlyUpdated() && installs == 0);
 observer.currentlyDownloadedVersion = @"not/a/version";
 assert(!helium::CurrentlyDownloadedReleaseNotesURL());
 puts("PASS: downloaded release URL capture, replacement, missing URL and no installation");
}}
'''
with tempfile.TemporaryDirectory(prefix='lune-release-notes-') as tmp:
    source = Path(tmp)/'test.mm'
    source.write_text(program)
    exe = Path(tmp)/'test'
    subprocess.run(['xcrun','clang++','-std=c++20','-fobjc-arc','-arch',a.arch,
                    '-mmacosx-version-min=13.0','-framework','AppKit',str(source),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
