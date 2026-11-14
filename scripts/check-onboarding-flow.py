#!/usr/bin/env python3
"""Validate the packaged setup flow using an isolated disposable profile."""
from pathlib import Path
from urllib.request import Request,urlopen
import json,subprocess,time,socket,sys,base64
import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path, help='Build directory containing Lune.app and chromedriver')
parser.add_argument('evidence', type=Path, help='Directory for reports and the disposable profile')
parser.add_argument('--skip-use-defaults', action='store_true', help='Skip the final shortcut that enables optional Helium services.')
args = parser.parse_args()
build = args.output.resolve()
out = args.evidence.resolve()
out.mkdir(parents=True, exist_ok=True)
profile=out/('profile-'+str(time.time_ns()));profile.mkdir(exist_ok=True)
# An existing empty preferences file prevents ChromeDriver's template from
# injecting search.suggest_enabled=false as an explicit user choice.
(profile/'Default').mkdir()
(profile/'Default/Preferences').write_text('{}\n')
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
log=(out/'driver.log').open('w');process=subprocess.Popen([str(build/'chromedriver'),f'--port={port}','--allowed-ips=127.0.0.1'],stdout=log,stderr=subprocess.STDOUT)
def wd(method,path,data=None):
 with urlopen(Request(f'http://127.0.0.1:{port}'+path,method=method,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'}),timeout=120) as res:
  value=json.load(res)['value']
  if isinstance(value,dict) and 'error' in value:raise RuntimeError(value)
  return value
for _ in range(100):
 try:
  if wd('GET','/status')['ready']:break
 except OSError:time.sleep(.1)
session=wd('POST','/session',{'capabilities':{'alwaysMatch':{'goog:chromeOptions':{'binary':str(build/'Lune.app/Contents/MacOS/Lune'),'args':['--headless=new','--disable-background-networking','--use-mock-keychain','--password-store=basic','--custom-update-server-url=http://127.0.0.1:1/','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',f'--user-data-dir={profile}']}}}})
p='/session/'+session['sessionId']; report={}
def js(script,async_=False):return wd('POST',p+('/execute/async' if async_ else '/execute/sync'),{'script':script,'args':[]})
def wait(script):
 for _ in range(100):
  try:
   value=js(script)
   if value:return value
  except Exception:pass
  time.sleep(.1)
 report['timeout']={'script':script,'url':wd('GET',p+'/url'),'body':js('return document.body.innerText'),'html':js('return document.documentElement.outerHTML.slice(0,6000)')}
 screenshot('timeout')
 raise RuntimeError('Timeout: '+script)
def nav(url):wd('POST',p+'/url',{'url':url})
def next_():js("document.querySelector('#setup-buttons button:last-child').click()")
def screenshot(name):(out/(name+'.png')).write_bytes(base64.b64decode(wd('GET',p+'/screenshot')))
try:
 nav('chrome://setup/')
 wait("return document.querySelector('#welcome-page input')?.checked")
 report['rootBackground']=js('return [document.documentElement,document.body,document.querySelector("main")].map(e=>getComputedStyle(e).backgroundColor)'); assert len(set(report['rootBackground']))==1
 report['tabTitle']=js('return document.title'); assert report['tabTitle']=='Welcome to Lune'
 report['welcome']=js("return {title:document.querySelector('h1').innerText,body:document.querySelector('.description').innerText,buttons:[...document.querySelectorAll('.welcome-actions button')].map(b=>b.innerText),updates:document.querySelector('input').checked,font:getComputedStyle(document.querySelector('h1')).fontFamily};")
 assert report['welcome']['title']=='setup lune'; assert report['welcome']['buttons']==['Setup','Use defaults']
 report['welcomeStyle']=js("return {background:getComputedStyle(document.querySelector('.setup-wallpaper'),'::before').backgroundImage,animation:getComputedStyle(document.querySelector('.setup-wallpaper'),'::before').animationName,policyLineHeight:getComputedStyle(document.querySelector('.policy')).lineHeight,weight:getComputedStyle(document.querySelector('.primary')).fontWeight,padding:[getComputedStyle(document.querySelector('.primary')).paddingLeft,getComputedStyle(document.querySelector('.primary')).paddingRight],synthesis:getComputedStyle(document.querySelector('.primary')).fontSynthesis,color:getComputedStyle(document.querySelector('.primary')).backgroundColor,credit:getComputedStyle(document.querySelector('.upstream-credit')).fontSize,security:document.querySelector('.updates p')!==null,remoteAssets:performance.getEntriesByType('resource').filter(r=>/^https?:/.test(r.name)).map(r=>r.name)}")
 report['wallpaperScheme']=js("return matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'")
 assert f"chrome://setup/wallpaper-{report['wallpaperScheme']}.jpg" in report['welcomeStyle']['background']
 assert report['welcomeStyle']['animation']=='wallpaper-in, wallpaper-rise'
 assert report['welcomeStyle']['policyLineHeight']=='13.2px'
 assert report['welcomeStyle']['weight']=='400'
 assert report['welcomeStyle']['padding']==['20px','16px']
 assert js("return [...document.querySelectorAll('.welcome-actions button')].every(b=>getComputedStyle(b).fontSize==='16px' && getComputedStyle(b).fontWeight==='400')")
 assert not report['welcomeStyle']['security']
 assert not report['welcomeStyle']['remoteAssets']
 wait("return getComputedStyle(document.querySelector('.welcome-content')).opacity === '1'")
 report['introTiming']=js("return document.getAnimations().map(a=>({name:a.animationName,duration:a.effect.getTiming().duration,delay:a.effect.getTiming().delay}))")
 assert len([a for a in report['introTiming'] if 'welcome-in' in a['name']])==1
 assert next(a for a in report['introTiming'] if 'welcome-in' in a['name'])['duration']==1500
 assert next(a for a in report['introTiming'] if 'welcome-in' in a['name'])['delay']==2000
 assert next(a for a in report['introTiming'] if a['name']=='wallpaper-in')['duration']==1600
 assert next(a for a in report['introTiming'] if a['name']=='wallpaper-in')['delay']==1300
 report['introMotion']=js("const a=document.getAnimations().find(a=>a.animationName.includes('welcome-rise'));const scale=document.getAnimations().find(a=>a.animationName.includes('logo-settle'));a.pause();scale.pause();a.currentTime=0;scale.currentTime=0;const logo=document.querySelector('#welcome-page-container svg[aria-label=Lune]');const start=logo.getBoundingClientRect();a.currentTime=3500;scale.currentTime=3500;const end=logo.getBoundingClientRect();return {startCenter:start.y+start.height/2,endCenter:end.y+end.height/2,height:innerHeight,duration:a.effect.getTiming().duration,delay:a.effect.getTiming().delay}")
 # Shorter Welcome copy can select the content-relative animation offset.
 # Keep the logo above center in the upper-middle region, without pinning the
 # regression to the removed defaults note's exact content height.
 assert .3*report['introMotion']['height'] < report['introMotion']['startCenter'] < .5*report['introMotion']['height'],report['introMotion']
 assert report['introMotion']['endCenter']<report['introMotion']['startCenter']
 assert report['introMotion']['duration']==3300 and report['introMotion']['delay']==200
 screenshot('welcome')
 js("document.querySelector('input').click()")
 js("document.querySelector('.welcome-actions .primary').click()")
 wait("return document.querySelector('#services-page.visible')")
 report['services']=js("return document.querySelector('#services-page').innerText")
 assert 'browser updates' not in report['services'].lower()
 assert js("return document.querySelector('#services-page button[role=switch]').getAttribute('aria-checked')") == 'true'
 wait("const b=document.querySelectorAll('#services-page button[role=switch]')[1];return !b.disabled && b.getAttribute('aria-checked')==='true'")
 js("document.querySelectorAll('#services-page button[role=switch]')[1].click()")
 wait("return document.querySelectorAll('#services-page button[role=switch]')[1].getAttribute('aria-checked')==='false'")
 js("document.querySelectorAll('#services-page button[role=switch]')[0].click()")
 wait("return document.querySelectorAll('#services-page button[role=switch]')[1].disabled")
 js("document.querySelectorAll('#services-page button[role=switch]')[0].click()")
 wait("return !document.querySelectorAll('#services-page button[role=switch]')[1].disabled")
 assert js("return document.querySelectorAll('#services-page button[role=switch]')[1].getAttribute('aria-checked')") == 'false'
 js("document.querySelectorAll('#services-page button[role=switch]')[0].click()")
 wait("return document.querySelectorAll('#services-page button[role=switch]')[1].disabled")
 report['customServicesUpdates']={'initially_on':True,'disabled_with_services_off':True,'explicit_off_choice_retained':True}
 next_();wait("return document.querySelector('#search-engines-page.visible button[aria-pressed=true]')")
 report['defaultSearch']=js("return document.querySelector('#search-engines-page button[aria-pressed=true]').innerText")
 assert report['defaultSearch'].startswith('Startpage')
 report['searchSuggestionsInitiallyOn']=js("return document.querySelector('#search-engines-page button[role=switch]').getAttribute('aria-checked')")
 assert report['searchSuggestionsInitiallyOn']=='true'
 wait("return getComputedStyle(document.querySelector('#search-engines-page')).opacity==='1' && !document.querySelector('#welcome-page') && !document.querySelector('#services-page')")
 screenshot('search')
 js("document.querySelector('#search-engines-page button[role=switch]').click()")
 wait("return document.querySelector('#search-engines-page button[role=switch]').getAttribute('aria-checked')==='false'")
 report['searchOrder']=js("return [...document.querySelectorAll('#search-engines-page button[aria-pressed]')].slice(0,3).map(b=>b.innerText.split('\\n')[0])")
 assert report['searchOrder']==['Startpage','Kagi','DuckDuckGo']
 js("[...document.querySelectorAll('#search-engines-page button')].find(b=>b.innerText.startsWith('DuckDuckGo')).click()")
 next_();wait("return document.querySelector('#import-page.visible, #data-import-page.visible') || document.querySelector('.onboarding-page.visible')?.innerText.includes('Import from')")
 report['importGraphic']=wait("const img=document.querySelector('.helium-icon img'); return img?.complete && img.naturalWidth ? img.getAttribute('src') : false")
 assert report['importGraphic']=='/lune-app.svg'
 assert js("return document.querySelector('#setup-buttons button:last-child').innerText") == 'Next'
 assert js("return document.querySelector('#setup-buttons button:last-child svg') !== null")
 report['beforeAppearanceWidth']=js('return innerWidth')
 next_();wait("return document.querySelector('#finish-page.visible')")
 time.sleep(.6)
 report['appearanceWidth']=js('return innerWidth')
 report['finish']=js("return {title:document.querySelector('#finish-page h2').innerText,buttons:[...document.querySelectorAll('#setup-buttons button')].map(b=>b.innerText)}")
 assert report['finish']['title']=='Customize Lune'
 report['dropdowns']=js("return [...document.querySelectorAll('#finish-page select')].map(s=>({label:s.getAttribute('aria-label'),value:s.value,options:[...s.options].map(o=>({value:o.value,label:o.label}))}))")
 assert [d['label'] for d in report['dropdowns']]==['Appearance','Theme','Tab sidebar','Show toolbar']
 assert [v['label'] for v in report['dropdowns'][1]['options'][:2]]==['System','Lune']
 assert len(report['dropdowns'][1]['options'])==16
 assert report['dropdowns'][1]['value']=='lune'
 def select(label,value):
  js("const s=document.querySelector('#finish-page select[aria-label="+json.dumps(label)+"]');s.value="+json.dumps(value)+";s.dispatchEvent(new Event('change',{bubbles:true}));")
  wait("return document.querySelector('#finish-page select[aria-label="+json.dumps(label)+"]')?.value === "+json.dumps(value))
  state=js("const done=arguments[arguments.length-1];const old=cr.webUIResponse;cr.webUIResponse=(id,ok,value)=>{if(id==='palette-test'){cr.webUIResponse=old;done(value)}else old(id,ok,value)};chrome.send('getOnboardingAppearance',['palette-test']);",True)
  if label=='Theme':assert state['theme']==value,(label,value,state)
  if label=='Appearance':assert str(state['scheme'])==value,(label,value,state)
 report['backgroundsByAppearance']={}
 for value in ['2','1','0']:
  select('Appearance',value)
  colors=js('return [document.documentElement,document.body,document.querySelector("main")].map(e=>getComputedStyle(e).backgroundColor)')
  assert len(set(colors))==1,colors
  report['backgroundsByAppearance'][value]=colors
 for option in report['dropdowns'][1]['options']:select('Theme',option['value'])
 select('Theme','lune')
 assert [o['label'] for o in report['dropdowns'][3]['options']]==['On hover edge','On hover sidebar','Always']
 select('Show toolbar','always');select('Show toolbar','hover');select('Show toolbar','no-hover');select('Show toolbar','always')
 select('Tab sidebar','right');select('Tab sidebar','left');select('Tab sidebar','right')
 assert report['finish']['buttons']==['Back','Done']
 assert report['appearanceWidth'] < report['beforeAppearanceWidth']
 assert js("return !!document.querySelector('#setup-buttons button:last-child svg')")
 screenshot('finish')
 js("document.querySelector('#setup-buttons button:first-child').click()");wait("return document.querySelector('#data-import-page.visible')")
 time.sleep(.5)
 report['afterBackWidth']=js('return innerWidth')
 assert report['afterBackWidth']==report['beforeAppearanceWidth']
 next_();wait("return document.querySelector('#finish-page.visible')")
 time.sleep(.5)
 next_();time.sleep(.5);report['doneUrl']=wd('GET',p+'/url');assert report['doneUrl'] in ('chrome://newtab/','chrome://new-tab-page/')
 nav('chrome://settings/')
 wait('return !!chrome.settingsPrivate')
 report['preferences']=js("const done=arguments[arguments.length-1]; chrome.settingsPrivate.getAllPrefs(p=>done(Object.fromEntries(p.filter(p=>['search.suggest_enabled','helium.completed_onboarding','helium.services.enabled','helium.services.browser_updates','helium.services.component_updates','helium.browser.vertical_right_aligned','side_panel.is_right_aligned','helium.browser.zen_mode_top_chrome_pinned','helium.browser.top_controls_overlay'].includes(p.key)).map(p=>[p.key,p.value]))));",True)
 nav('chrome://settings/appearance')
 wait("const find=(r)=>r.querySelector('settings-appearance-page')||[...r.querySelectorAll('*')].map(e=>e.shadowRoot&&find(e.shadowRoot)).find(Boolean);return !!find(document)")
 report['independentPanelControl']=js("const find=(r)=>r.querySelector('#sidePanelPosition')||[...r.querySelectorAll('*')].map(e=>e.shadowRoot&&find(e.shadowRoot)).find(Boolean);return !!find(document)")
 assert report['independentPanelControl'] is False
 nav('chrome://prefs-internals/helium.completed_onboarding')
 report['completed']=json.loads(js('return document.body.innerText'))
 assert report['completed'] is True
 assert report['preferences']['helium.browser.vertical_right_aligned'] is True
 assert report['preferences']['side_panel.is_right_aligned'] is False
 assert report['preferences']['helium.browser.zen_mode_top_chrome_pinned'] is True
 assert report['preferences']['helium.browser.top_controls_overlay'] is False
 assert report['preferences']['search.suggest_enabled'] is False
 assert report['preferences']['helium.services.enabled'] is False
 assert report['preferences']['helium.services.browser_updates'] is False
 assert report['preferences']['helium.services.component_updates'] is False
 nav('chrome://setup/');wait("return document.querySelector('#welcome-page input') && !document.querySelector('#welcome-page input').checked")
 js("document.querySelector('.welcome-actions .primary').click()")
 wait("return document.querySelector('#services-page.visible')");next_();wait("return document.querySelector('#search-engines-page.visible button[aria-pressed=true]')")
 report['retainedSearch']=js("return document.querySelector('#search-engines-page button[aria-pressed=true]').innerText")
 assert report['retainedSearch'].startswith('DuckDuckGo')
 assert js("return document.querySelector('#search-engines-page button[role=switch]').getAttribute('aria-checked')") == 'false'
 if not args.skip_use_defaults:
  nav('chrome://setup/');wait("return document.querySelector('#welcome-page input') && !document.querySelector('#welcome-page input').checked")
  js("document.querySelector('input').click(); document.querySelector('.welcome-actions .ghost').click()")
  wait("return location.href.includes('newtab') || location.href.includes('new-tab-page')")
  nav('chrome://settings/');wait('return !!chrome.settingsPrivate')
  report['defaultsUpdates']=js("const done=arguments[arguments.length-1];chrome.settingsPrivate.getPref('helium.services.browser_updates',p=>done(p.value));",True)
  assert report['defaultsUpdates'] is True
  report['defaultsServices']=js("const done=arguments[arguments.length-1];chrome.settingsPrivate.getPref('helium.services.enabled',p=>done(p.value));",True)
  assert report['defaultsServices'] is True
  report['defaultsServicesUpdates']=js("const done=arguments[arguments.length-1];chrome.settingsPrivate.getPref('helium.services.component_updates',p=>done(p.value));",True)
  assert report['defaultsServicesUpdates'] is True
  report['defaultsSearchSuggestions']=js("const done=arguments[arguments.length-1];chrome.settingsPrivate.getPref('search.suggest_enabled',p=>done(p.value));",True)
  assert report['defaultsSearchSuggestions'] is True
  nav('chrome://setup/');wait("return document.querySelector('#welcome-page input')?.checked")
  js("document.querySelector('input').click(); document.querySelector('.welcome-actions .ghost').click()")
  wait("return location.href.includes('newtab') || location.href.includes('new-tab-page')")
  nav('chrome://settings/');wait('return !!chrome.settingsPrivate')
  assert js("const done=arguments[arguments.length-1];chrome.settingsPrivate.getPref('helium.services.browser_updates',p=>done(p.value));",True) is False
  assert js("const done=arguments[arguments.length-1];chrome.settingsPrivate.getPref('helium.services.component_updates',p=>done(p.value));",True) is True
  report['defaultsServicesUpdatesIndependentOfBrowserOptOut']=True
 else:
  report['useDefaultsConsentBranch']='skipped; services remain disabled'
 report['pass']=True
finally:
 (out/'report.json').write_text(json.dumps(report,indent=2))
 wd('DELETE',p);process.terminate();log.close()
print(json.dumps(report,indent=2))
