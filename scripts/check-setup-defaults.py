#!/usr/bin/env python3
"""Check fresh defaults parity, acceptance boundaries and retained opt-outs."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import argparse,base64,json,socket,subprocess,time,sys

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('output',type=Path)
parser.add_argument('evidence',type=Path)
args=parser.parse_args()
build=args.output.resolve();out=args.evidence.resolve();out.mkdir(parents=True,exist_ok=True)
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
log=(out/'driver.log').open('w');driver=subprocess.Popen([str(build/'chromedriver'),f'--port={port}','--allowed-ips=127.0.0.1'],stdout=log,stderr=subprocess.STDOUT)
def wd(method,path,data=None):
 req=Request(f'http://127.0.0.1:{port}'+path,method=method,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
 try:
  with urlopen(req,timeout=120) as res:value=json.load(res)['value']
 except HTTPError as e:raise RuntimeError(e.read().decode()) from e
 if isinstance(value,dict) and 'error' in value:raise RuntimeError(value)
 return value
for _ in range(100):
 try:
  if wd('GET','/status')['ready']:break
 except OSError:time.sleep(.1)
keys=['search.suggest_enabled','helium.completed_onboarding','helium.services.enabled','helium.services.user_consented','helium.services.browser_updates','helium.services.component_updates','helium.services.ext_proxy','helium.services.bangs','helium.services.ublock_assets','helium.services.spellcheck_files','helium.browser.vertical_right_aligned','helium.browser.zen_mode_top_chrome_pinned','helium.browser.top_controls_overlay','helium.browser.top_controls_hover_disabled']
p=None

def start(name,profile=None):
 global p,setup_handle,inspector_handle
 profile=profile or out/(name+'-profile-'+str(time.time_ns()))
 pref_file=profile/'Default/Preferences'
 if not pref_file.exists():
  # Skip ChromeDriver's template opt-outs; retain actual user choices on restart.
  pref_file.parent.mkdir(parents=True,exist_ok=True)
  pref_file.write_text('{}\n')
 session=wd('POST','/session',{'capabilities':{'alwaysMatch':{'goog:chromeOptions':{'binary':str(build/'Lune.app/Contents/MacOS/Lune'),'args':['--disable-background-networking','--use-mock-keychain','--password-store=basic','--window-size=1100,800','--custom-update-server-url=http://127.0.0.1:1/','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',f'--user-data-dir={profile}']}}}})
 p='/session/'+session['sessionId'];setup_handle=wd('GET',p+'/window')
 inspector_handle=wd('POST',p+'/window/new',{'type':'tab'})['handle']
 wd('POST',p+'/window',{'handle':inspector_handle});wd('POST',p+'/url',{'url':'chrome://settings/'})
 wait('return !!chrome.settingsPrivate');wd('POST',p+'/window',{'handle':setup_handle})
 nav_setup()
 (out/'session.json').write_text(json.dumps({'port':port,'prefix':p,'driver_pid':driver.pid,'profile':str(profile),'binary':str(build/'Lune.app')}))
 return profile

def js(script,async_=False):return wd('POST',p+('/execute/async' if async_ else '/execute/sync'),{'script':script,'args':[]})
def wait(script):
 for _ in range(150):
  value=js(script)
  if value:return value
  time.sleep(.1)
 raise AssertionError('Timeout: '+script)
def nav_setup():
 wd('POST',p+'/url',{'url':'chrome://setup/'});wait("return !!document.querySelector('#welcome-page input')")
def click(selector):js('document.querySelector('+json.dumps(selector)+').click()')
def step(name):wait('return !!document.querySelector('+json.dumps('#'+name+'-page.visible')+')')
def next_():click('#setup-buttons button:last-child')
def checked(selector):return js('return document.querySelector('+json.dumps(selector)+').getAttribute("aria-checked")')=='true'
def prefs():
 wd('POST',p+'/window',{'handle':inspector_handle})
 value=js('const done=arguments[arguments.length-1];chrome.settingsPrivate.getAllPrefs(p=>done(Object.fromEntries(p.filter(p=>'+json.dumps(keys)+'.includes(p.key)).map(p=>[p.key,p.value]))));',True)
 wd('POST',p+'/window',{'handle':setup_handle});return value

def close():
 global p
 wd('DELETE',p);p=None

def finish_from_search(services):
 next_();step('data-import');next_()
 if services:step('password-manager');next_()
 step('finish')
 appearance=wait("return document.querySelectorAll('#finish-page select').length===4 && [...document.querySelectorAll('#finish-page select')].map(s=>s.value)")
 assert appearance==['0','lune','left','hover'],appearance
 next_();wait("return location.href.includes('newtab') || location.href.includes('new-tab-page')")

def shot(name):
 wait("return !document.getAnimations().some(a=>a.playState==='running' && a.effect.getTiming().iterations!==Infinity)")
 (out/(name+'.png')).write_bytes(base64.b64decode(wd('GET',p+'/screenshot')))
report={}
try:
 start('defaults')
 before=prefs();assert before['helium.services.user_consented'] is False and before['search.suggest_enabled'] is False
 click('.welcome-actions .ghost');wait("return location.href.includes('newtab') || location.href.includes('new-tab-page')")
 report['useDefaults']=prefs();close()
 start('unchanged-custom')
 click('.welcome-actions .primary');step('services')
 assert checked('#services-page button[role=switch]')
 assert js("return [...document.querySelectorAll('#services-page button[role=switch]')].every(b=>b.getAttribute('aria-checked')==='true' && !b.disabled)")
 before=prefs();assert before['helium.services.user_consented'] is False and before['search.suggest_enabled'] is False
 report['servicesBeforeNext']=before
 report['descriptionStyle']=js("return {description:getComputedStyle(document.querySelector('#services-page .toggle-text p')).fontSize,subtitle:getComputedStyle(document.querySelector('#services-page .page-header p')).fontSize}")
 assert report['descriptionStyle']=={'description':'14px','subtitle':'16px'}
 shot('services-defaults')
 next_();step('search-engines');assert checked('#search-engines-page button[role=switch]')
 before=prefs();assert before['helium.services.user_consented'] is True and before['search.suggest_enabled'] is False
 report['suggestionsBeforeNext']=before
 assert js("return getComputedStyle(document.querySelector('.engine-text p')).fontSize")=='14px'
 shot('search-defaults')
 finish_from_search(True);report['unchangedCustom']=prefs()
 assert report['useDefaults']==report['unchangedCustom'],(report['useDefaults'],report['unchangedCustom']);close()
 profile=start('opt-outs')
 click('#welcome-page input');click('.welcome-actions .primary');step('services')
 assert checked('#services-page button[role=switch]')
 assert checked('#services-page button[role=switch]:nth-child(2)')
 click('#services-page button[role=switch]:nth-child(2)')
 click('#services-page button[role=switch]')
 wait("return document.querySelectorAll('#services-page button[role=switch]')[1].disabled")
 click('#setup-buttons button:first-child');step('welcome');click('.welcome-actions .primary');step('services')
 assert not checked('#services-page button[role=switch]')
 nav_setup();click('.welcome-actions .primary');step('services');assert not checked('#services-page button[role=switch]')
 next_();step('search-engines');assert checked('#search-engines-page button[role=switch]')
 click('#search-engines-page button[role=switch]');wait("return document.querySelector('#search-engines-page button[role=switch]').getAttribute('aria-checked')==='false'")
 assert prefs()['search.suggest_enabled'] is False
 close();start('opt-outs-resumed',profile)
 assert js("return document.querySelector('#welcome-page input').checked") is False
 click('.welcome-actions .primary');step('services');assert not checked('#services-page button[role=switch]')
 assert not checked('#services-page button[role=switch]:nth-child(2)')
 next_();step('search-engines');assert not checked('#search-engines-page button[role=switch]')
 finish_from_search(False);report['retainedOptOuts']=prefs()
 for k in ['search.suggest_enabled','helium.services.enabled','helium.services.component_updates','helium.services.browser_updates']:assert report['retainedOptOuts'][k] is False
 report['backReloadAndRestartPreserveChoices']=True;close()
 start('review')
 click('.welcome-actions .primary');step('services');shot('review')
 report['pass']=True
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
finally:
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 if p:close()
 driver.terminate();driver.wait(timeout=10);log.close()
