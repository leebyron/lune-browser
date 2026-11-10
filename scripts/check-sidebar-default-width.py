from pathlib import Path
from urllib.request import Request,urlopen
import json,subprocess,time,socket,sys
import argparse,tempfile
parser=argparse.ArgumentParser(description='Verify actual sidebar layout width and preservation of a saved custom width.')
parser.add_argument('build',type=Path)
parser.add_argument('--saved-width',type=int)
parser.add_argument('--report',type=Path,required=True)
args=parser.parse_args()
tmp=tempfile.TemporaryDirectory(prefix='lune-sidebar-width-');out=Path(tmp.name);build=args.build.resolve()
expected_width=args.saved_width if args.saved_width is not None else 216
profile=out/('profile-'+str(time.time_ns()));(profile/'Default').mkdir(parents=True)
(profile/'Default/Preferences').write_text(json.dumps({'helium':{'completed_onboarding':True,'browser':{'zen_mode_sidebar_pinned':False},'services':{'enabled':False,'browser_updates':False}}}))
if args.saved_width is not None:
 prefs=json.loads((profile/'Default/Preferences').read_text());prefs['vertical_tabs']={'uncollapsed_width':expected_width};(profile/'Default/Preferences').write_text(json.dumps(prefs))
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
def request(port,method,path,data=None):
 with urlopen(Request(f'http://127.0.0.1:{port}'+path,method=method,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'}),timeout=120) as response:return json.load(response)['value']
log=(out/'driver.log').open('w');driver=subprocess.Popen([str(build/'chromedriver'),f'--port={port}','--allowed-ips=127.0.0.1'],stdout=log,stderr=subprocess.STDOUT)
def wd(method,path,data=None):return request(port,method,path,data)
for _ in range(100):
 try:
  if wd('GET','/status')['ready']:break
 except OSError:time.sleep(.1)
cap={'goog:chromeOptions':{'binary':str(build/'Lune.app/Contents/MacOS/Lune'),'args':['--headless=new','--disable-background-networking','--use-mock-keychain','--password-store=basic','--custom-update-server-url=http://127.0.0.1:1/',f'--user-data-dir={profile}']}}
s=wd('POST','/session',{'capabilities':{'alwaysMatch':cap}});sid='/session/'+s['sessionId'];report={}
def js(script,async_=False):return wd('POST',sid+('/execute/async' if async_ else '/execute/sync'),{'script':script,'args':[]})
def pref(key,value):
 result=js('chrome.settingsPrivate.setPref('+json.dumps(key)+','+json.dumps(value)+',arguments[arguments.length-1])',True);assert result is True,result;time.sleep(.3)
try:
 wd('POST',sid+'/window/rect',{'width':1200,'height':800})
 wd('POST',sid+'/url',{'url':'chrome://settings/appearance'})
 for _ in range(100):
  if js('return !!chrome.settingsPrivate'):break
  time.sleep(.1)
 report['unpin']=js('return innerWidth')
 pref('helium.browser.zen_mode_sidebar_pinned',True);report['pin']=js('return innerWidth')
 report['reservedWidth']=report['unpin']-report['pin'];assert report['reservedWidth']==expected_width,report
 pref('helium.browser.vertical_right_aligned',True);report['pinRight']=js('return innerWidth');assert report['pinRight']==report['pin']
 pref('helium.browser.zen_mode_sidebar_pinned',False);report['unpinRight']=js('return innerWidth');assert report['unpinRight']==report['unpin']
 pref('helium.browser.vertical_right_aligned',False)
 report['passed']=True
finally:
 args.report.write_text(json.dumps(report,indent=2));wd('DELETE',sid);driver.terminate();log.close()
print(json.dumps(report,indent=2))
