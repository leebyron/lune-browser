"""Exercise clean-exit restoration and a saved New Tab choice in isolated profiles.

Set saved preferences through Settings so Chromium maintains protected-pref hashes.
Requires the repository build environment (requests) and matching ChromeDriver.
"""
import argparse,http.server,json,socket,subprocess,threading,time
from pathlib import Path
import requests
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--directory',type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.directory.mkdir(parents=True,exist_ok=False)
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  body=(b'<?xml version="1.0"?><rss version="2.0"><channel/></rss>' if self.path=='/no-update.xml' else ('<title>'+self.path+'</title><p>Session restore fixture</p>').encode())
  self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
log=(a.directory/'driver.log').open('w');driver=subprocess.Popen([str(a.output/'chromedriver'),f'--port={port}','--allowed-ips=127.0.0.1'],stdout=log,stderr=subprocess.STDOUT)
def wd(method,path,data=None):
 r=requests.request(method,f'http://127.0.0.1:{port}'+path,json=data,timeout=60);value=r.json()['value']
 if isinstance(value,dict) and 'error' in value:raise RuntimeError(value)
 return value
for _ in range(100):
 try:
  if wd('GET','/status')['ready']:break
 except requests.RequestException:time.sleep(.1)
else:raise RuntimeError('Driver not ready')
results=[]
try:
 for label,saved in [('default',None),('saved-new-tab',5)]:
  case=a.directory/label;profile=case/'profile';(profile/'Default').mkdir(parents=True)
  prefs={'helium':{'completed_onboarding':True,'services':{'enabled':False,'browser_updates':False}}}
  (profile/'Default/Preferences').write_text(json.dumps(prefs));urls=[origin+'/saved-a',origin+'/saved-b'];row={'case':label,'saved_choice':saved}
  for phase in ('write','reopen'):
   active=profile/'DevToolsActivePort'
   if active.exists():active.unlink()
   blog=(case/f'{phase}.log').open('w')
   cmd=[str(a.output/'Lune.app/Contents/MacOS/Lune'),'--headless=new','--remote-debugging-port=0',f'--user-data-dir={profile}','--no-first-run','--no-default-browser-check','--disable-background-networking','--use-mock-keychain','--password-store=basic',f'--custom-update-server-url={origin}/no-update.xml']
   if phase=='write':cmd.append(urls[0])
   browser=subprocess.Popen(cmd,stdout=blog,stderr=subprocess.STDOUT)
   for _ in range(200):
    if browser.poll() is not None:raise RuntimeError(f'{label} {phase}: browser exited')
    if active.exists() and active.read_text().splitlines():break
    time.sleep(.1)
   else:raise RuntimeError('No DevTools port')
   debug=int(active.read_text().splitlines()[0]);session=wd('POST','/session',{'capabilities':{'alwaysMatch':{'goog:chromeOptions':{'debuggerAddress':f'127.0.0.1:{debug}'}}}});sid='/session/'+session['sessionId']
   def js(code):return wd('POST',sid+'/execute/async',{'script':code,'args':[]})
   if phase=='write':
    original=wd('GET',sid+'/window');tab=wd('POST',sid+'/window/new',{'type':'tab'})['handle'];wd('POST',sid+'/window',{'handle':tab});wd('POST',sid+'/url',{'url':urls[1]})
    settings=wd('POST',sid+'/window/new',{'type':'tab'})['handle'];wd('POST',sid+'/window',{'handle':settings});wd('POST',sid+'/url',{'url':'chrome://settings/onStartup'})
    if saved is not None:
     assert js('chrome.settingsPrivate.setPref("session.restore_on_startup", '+str(saved)+', arguments[arguments.length-1])') is True
    observed=js('chrome.settingsPrivate.getPref("session.restore_on_startup", arguments[arguments.length-1])');row['effective_startup_choice']=observed['value'];assert observed['value']==(1 if saved is None else saved),observed
    wd('DELETE',sid+'/window');wd('POST',sid+'/window',{'handle':original})
   else:
    for _ in range(100):
     targets=requests.get(f'http://127.0.0.1:{debug}/json/list',timeout=10).json();pages=[t.get('url') for t in targets if t.get('type')=='page']
     if saved is not None or all(url in pages for url in urls):break
     time.sleep(.1)
    row['restored_fixture_pages']=[url.removeprefix(origin) for url in urls if url in pages]
    assert (all(url in pages for url in urls) if saved is None else not any(url in pages for url in urls)),row
   # Browser.close uses Chromium's orderly quit path, rather than a signal/crash.
   try:wd('POST',sid+'/goog/cdp/execute',{'cmd':'Browser.close','params':{}})
   except (RuntimeError,requests.RequestException):pass
   browser.wait(timeout=30);blog.close();assert browser.returncode==0,browser.returncode
   stored=json.loads((profile/'Default/Preferences').read_text());row[phase+'_exit_type']=stored.get('profile',{}).get('exit_type');assert row[phase+'_exit_type']=='Normal',row
   try:wd('DELETE',sid)
   except (RuntimeError,requests.RequestException):pass
  row['passed']=True;results.append(row);print(json.dumps(row),flush=True)
  (a.directory/'report.json').write_text(json.dumps({'passed':all(r['passed'] for r in results),'cases':results},indent=2)+'\n')
finally:
 if 'browser' in globals() and browser.poll() is None:
  browser.terminate();browser.wait(timeout=10)
 driver.terminate();driver.wait(timeout=10);log.close();server.shutdown()
