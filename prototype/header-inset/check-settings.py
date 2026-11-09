#!/usr/bin/env python3
"""Exercise the real Settings dropdowns, pref synchronization and saved state."""
import argparse
import json
import socket
import subprocess
import time
from pathlib import Path
from urllib.request import Request, ProxyHandler, build_opener

parser = argparse.ArgumentParser()
parser.add_argument('output', type=Path)
parser.add_argument('evidence', type=Path)
args = parser.parse_args()
out, evidence = args.output.resolve(), args.evidence.resolve()
evidence.mkdir(parents=True, exist_ok=True)
profile = evidence/'profile'
assert not profile.exists(), 'Use a fresh evidence directory'
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
opener = build_opener(ProxyHandler({}))
def wd(method, path, body=None):
    req = Request(f'http://127.0.0.1:{port}'+path, method=method,
                  data=None if body is None else json.dumps(body).encode(),
                  headers={'Content-Type':'application/json'})
    with opener.open(req, timeout=90) as response:
        value = json.load(response)['value']
    if isinstance(value, dict) and 'error' in value:
        raise RuntimeError(value)
    return value
log = (evidence/'driver.log').open('w')
driver = subprocess.Popen([str(out/'chromedriver'), f'--port={port}'], stdout=log, stderr=subprocess.STDOUT)
report = {}
sid = None
try:
    for _ in range(100):
        try:
            if wd('GET','/status')['ready']:
                break
        except OSError:
            time.sleep(.1)
    def launch():
        value = wd('POST','/session',{'capabilities':{'alwaysMatch':{'goog:chromeOptions':{
            'binary':str(out/'Lune.app/Contents/MacOS/Lune'),
            'args':['--headless=new','--lune-obscured-header-prototype',
                    '--disable-background-networking','--use-mock-keychain',
                    '--password-store=basic', f'--user-data-dir={profile}'],
            'prefs':{'helium.services.enabled':False,'helium.services.browser_updates':False}}}}})
        return '/session/'+value['sessionId']
    sid = launch()
    def js(script, *args):
        return wd('POST',sid+'/execute/sync',{'script':script,'args':list(args)})
    def async_js(script, *args):
        return wd('POST',sid+'/execute/async',{'script':script,'args':list(args)})
    def settings():
        wd('POST',sid+'/url',{'url':'chrome://settings/appearance'})
        for _ in range(100):
            ready=js('''window.deepFind=(selector,root=document)=>{
              const found=root.querySelector(selector); if(found)return found;
              for(const el of root.querySelectorAll('*')) {
                if(el.shadowRoot){const match=deepFind(selector,el.shadowRoot); if(match)return match;}
              } return null;};
              return !!deepFind('#showToolbar')?.shadowRoot?.querySelector('select');''')
            if ready:
                time.sleep(.2)
                return
            time.sleep(.1)
        raise AssertionError('Settings dropdowns did not render')
    def state():
        return js('''return Object.fromEntries(['showToolbar','sidebarPosition','sidePanelPosition'].map(id=>{
          const el=deepFind('#'+id), select=el.shadowRoot.querySelector('select');
          return [id,{label:el.label,value:select.value,disabled:select.disabled,
            options:[...select.options].filter(o=>!o.hidden && !o.disabled).map(o=>o.textContent.trim())}];
        }));''')
    def choose(id,value):
        js('''const el=deepFind('#'+arguments[0]), select=el.shadowRoot.querySelector('select');
          if(select.disabled)throw new Error('disabled');
          select.value=arguments[1]; select.dispatchEvent(new Event('change',{bubbles:true}));''',id,value)
        time.sleep(.3)
    def set_pref(key,value):
        assert async_js('''chrome.settingsPrivate.setPref(arguments[0],arguments[1],'',arguments[arguments.length-1]);''',key,value)
        time.sleep(.3)
    def prefs():
        return async_js('''const keys=['helium.browser.zen_mode_top_chrome_pinned',
          'helium.browser.top_controls_overlay','helium.browser.vertical_right_aligned','side_panel.is_right_aligned'];
          const done=arguments[arguments.length-1]; Promise.all(keys.map(key=>new Promise(resolve=>
          chrome.settingsPrivate.getPref(key,p=>resolve([key,p.value]))))).then(v=>done(Object.fromEntries(v)));''')
    settings()
    report['initial']=state()
    initial=report['initial']
    assert initial['showToolbar']['value']=='hover', initial
    assert initial['showToolbar']['label']=='Show toolbar'
    assert initial['showToolbar']['options']==['On hover','Always','Always cover (experimental)']
    assert initial['sidebarPosition']['label']=='Sidebar position'
    assert initial['sidebarPosition']['options']==['Left','Right']
    assert initial['sidePanelPosition']['disabled']
    report['changes']=[]
    for right in (True,False,True):
        choose('sidebarPosition',str(right).lower())
        for mode in ('always','cover','hover'):
            choose('showToolbar',mode)
            value=prefs(); ui=state()
            assert value['helium.browser.zen_mode_top_chrome_pinned']==(mode!='hover'),value
            assert value['helium.browser.top_controls_overlay']==(mode=='cover'),value
            assert value['helium.browser.vertical_right_aligned']==right,value
            assert value['side_panel.is_right_aligned']==(not right),value
            assert ui['sidePanelPosition']['value']==str(not right).lower(),ui
            report['changes'].append({'right':right,'mode':mode,'prefs':value})
    # Backend changes, including the native menu's two existing prefs, update UI.
    set_pref('helium.browser.top_controls_overlay',True)
    set_pref('helium.browser.zen_mode_top_chrome_pinned',True)
    assert state()['showToolbar']['value']=='cover'
    set_pref('helium.browser.vertical_right_aligned',False)
    assert state()['sidebarPosition']['value']=='false'
    assert state()['sidePanelPosition']['value']=='true'
    # A conflicting panel write cannot violate the sidebar relationship.
    set_pref('side_panel.is_right_aligned',False)
    assert prefs()['side_panel.is_right_aligned'] is True
    assert state()['sidePanelPosition']['value']=='true'
    report['external_writes']=state()
    choose('showToolbar','always')
    choose('sidebarPosition','true')
    wd('DELETE',sid); sid=None
    time.sleep(1)
    sid=launch(); settings()
    report['restart']=state()
    assert report['restart']['showToolbar']['value']=='always'
    assert report['restart']['sidebarPosition']['value']=='true'
    assert report['restart']['sidePanelPosition']['value']=='false'
    # Restore a deliberately conflicting saved panel position on startup.
    wd('DELETE',sid); sid=None
    time.sleep(1)
    saved=profile/'Default/Preferences'
    data=json.loads(saved.read_text())
    data.setdefault('side_panel',{})['is_right_aligned']=True
    saved.write_text(json.dumps(data))
    sid=launch(); settings()
    report['startup_repair']=state()
    assert report['startup_repair']['sidebarPosition']['value']=='true'
    assert report['startup_repair']['sidePanelPosition']['value']=='false'
    report['passed']=True
    (evidence/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: Settings labels/options, all modes, both sides, backend sync, panel invariant and restart')
finally:
    if sid:
        wd('DELETE',sid)
    driver.terminate(); driver.wait(timeout=20); log.close()
