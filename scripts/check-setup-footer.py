#!/usr/bin/env python3
"""Exercise setup navigation and real browser-overlay insets, leaving a preview."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import quote
import base64, json, socket, subprocess, sys, time

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('output', type=Path, help='Build directory containing Lune.app and chromedriver')
parser.add_argument('evidence', type=Path, help='Disposable test profile and report directory')
args = parser.parse_args()
build = args.output.resolve()
evidence = args.evidence.resolve()
evidence.mkdir(exist_ok=True)
profile = evidence/('profile-'+str(time.time_ns()))
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
log = (evidence/'driver.log').open('w')
driver = subprocess.Popen([str(build/'chromedriver'), f'--port={port}',
                           '--allowed-ips=127.0.0.1'], stdout=log, stderr=subprocess.STDOUT)
def wd(method, path, data=None):
    request = Request(f'http://127.0.0.1:{port}'+path, method=method,
                      data=None if data is None else json.dumps(data).encode(),
                      headers={'Content-Type':'application/json'})
    try:
        with urlopen(request, timeout=120) as response:
            value = json.load(response)['value']
    except HTTPError as error:
        raise RuntimeError(error.read().decode()) from error
    if isinstance(value, dict) and 'error' in value:
        raise RuntimeError(value)
    return value
for _ in range(100):
    try:
        if wd('GET', '/status')['ready']: break
    except OSError: time.sleep(.1)
try:
    session = wd('POST', '/session', {'capabilities': {'alwaysMatch': {
        'goog:chromeOptions': {'binary': str(build/'Lune.app/Contents/MacOS/Lune'),
            'args': ['--disable-background-networking', '--use-mock-keychain',
                     '--password-store=basic', '--window-size=1100,800',
                     '--custom-update-server-url=http://127.0.0.1:1/',
                     '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1',
                     f'--user-data-dir={profile}']}}}})
except Exception:
    driver.terminate()
    log.close()
    raise
prefix = '/session/'+session['sessionId']
(evidence/'session.json').write_text(json.dumps({'port':port, 'prefix':prefix,
    'driver_pid':driver.pid, 'profile':str(profile), 'binary':str(build/'Lune.app')}))
def js(script, async_=False):
    return wd('POST', prefix+('/execute/async' if async_ else '/execute/sync'),
              {'script':script, 'args':[]})
def wait(script):
    for _ in range(200):
        value = js(script)
        if value: return value
        time.sleep(.1)
    raise RuntimeError('Timeout: '+script)
def screenshot(name):
    (evidence/(name+'.png')).write_bytes(base64.b64decode(wd('GET', prefix+'/screenshot')))
def prefs():
    return js('''const done=arguments[arguments.length-1];
      const id='safe-area-probe-'+Math.random(), original=window.cr.webUIResponse;
      window.cr.webUIResponse=(response,success,value)=>{
        if(response===id){window.cr.webUIResponse=original;done(value);}
        else original(response,success,value);
      };
      chrome.send('getPrefs',[id]);''', True)
def dots():
    return js('''return [...document.querySelectorAll('.progress-step')].map(b=>({
      label:b.getAttribute('aria-label'),current:b.getAttribute('aria-current'),
      filled:b.classList.contains('filled'),disabled:b.disabled,
      dot:getComputedStyle(b.querySelector('.step-dot')).width,
      target:b.getBoundingClientRect().width}));''')
def goto(index, selector):
    js(f"document.querySelectorAll('.progress-step')[{index}].click()")
    wait(f'return !!document.querySelector({json.dumps(selector)})')
    time.sleep(.25)
def geometry():
    return js('''let probe=document.querySelector('#safe-area-probe');
      if(!probe){probe=document.createElement('div');probe.id='safe-area-probe';
        probe.style.cssText='position:fixed;visibility:hidden;padding-bottom:env(safe-area-inset-bottom);padding-top:env(safe-area-inset-top)';
        document.body.append(probe);}
      const footer=document.querySelector('#setup-footer'), rect=footer?.getBoundingClientRect();
      return {bottom:parseFloat(getComputedStyle(probe).paddingBottom),
        top:parseFloat(getComputedStyle(probe).paddingTop),height:innerHeight,width:innerWidth,
        footerBottom:rect ? innerHeight-rect.bottom : null,footerTop:rect?.top,
        viewport:document.querySelector('meta[name=viewport]')?.content,
        zoom:devicePixelRatio};''')

report={}
try:
    wd('POST',prefix+'/url',{'url':'chrome://setup/'})
    wait("return !!document.querySelector('.welcome-actions .primary')")
    report['welcomeArtwork']=js("return getComputedStyle(document.querySelector('.setup-wallpaper')).opacity")
    assert report['welcomeArtwork']=='1'
    report['welcomeDots']=dots()
    assert len(report['welcomeDots']) in (5,6) and report['welcomeDots'][0]['current']=='step'
    assert js("return document.querySelector('#setup-buttons')===null")
    js("document.querySelector('.welcome-actions .primary').click()")
    wait("return !!document.querySelector('#services-page.visible')")
    time.sleep(1)
    report['setupArtwork']=js("return getComputedStyle(document.querySelector('.setup-wallpaper')).opacity")
    assert report['setupArtwork']=='0.5'
    before=prefs()
    report['initialDots']=dots()
    assert len(report['initialDots'])==5,report['initialDots']
    assert report['initialDots'][1]['current']=='step'
    assert all(d['dot']=='8px' and d['target']==20 for d in dots())
    report['dotLayout']=js('''const dots=[...document.querySelectorAll('.step-dot')].map(d=>d.getBoundingClientRect());
      const nav=document.querySelector('.setup-progress').getBoundingClientRect();
      const buttons=document.querySelector('#setup-buttons').getBoundingClientRect();
      return {gap:dots[1].left-dots[0].right,belowButtons:nav.top>=buttons.bottom,
        nativeTitles:[...document.querySelectorAll('.progress-step')].some(b=>b.hasAttribute('title'))};''')
    assert report['dotLayout']=={'gap':12,'belowButtons':True,'nativeTitles':False},report['dotLayout']
    for scheme in ['light','dark']:
        wd('POST',prefix+'/goog/cdp/execute',{'cmd':'Emulation.setEmulatedMedia',
            'params':{'features':[{'name':'prefers-color-scheme','value':scheme}]}})
        style=js('''const s=getComputedStyle(document.querySelector('.step-tooltip'));
          return {foreground:s.color,background:s.backgroundColor,radius:s.borderRadius,weight:s.fontWeight,duration:s.transitionDuration,delay:s.transitionDelay};''')
        assert style=={'foreground':'rgb(255, 255, 255)','background':'rgb(0, 0, 0)','radius':'9999px','weight':'700','duration':'0s','delay':'0s'},style
        report['tooltip-'+scheme]=style
    wd('POST',prefix+'/goog/cdp/execute',{'cmd':'Emulation.setEmulatedMedia','params':{'features':[]}})
    report['footerEffects']=js('''const footer=document.querySelector('#setup-footer');
      const fade=document.querySelector('#setup-footer-fade');
      const tip=document.querySelector('.step-tooltip').getBoundingClientRect();
      const dot=document.querySelector('.step-dot').getBoundingClientRect();
      return {animation:getComputedStyle(footer).animationName,translate:getComputedStyle(footer).translate,
        tooltipGap:dot.top-tip.bottom,fadeBottom:innerHeight-fade.getBoundingClientRect().bottom,
        fadeBlocksInput:getComputedStyle(fade).pointerEvents!=='none'};''')
    assert report['footerEffects']=={'animation':'none','translate':'none','tooltipGap':5,'fadeBottom':0,'fadeBlocksInput':False},report['footerEffects']
    report['visibleAlert']=geometry()
    assert report['visibleAlert']['bottom']>0, report['visibleAlert']
    assert abs(report['visibleAlert']['footerBottom']-report['visibleAlert']['bottom']-10)<1
    report['verticalSpacing']=js('''const dot=document.querySelector('.step-dot').getBoundingClientRect();
      const buttons=document.querySelector('#setup-buttons').getBoundingClientRect();
      const inset=parseFloat(getComputedStyle(document.querySelector('#safe-area-probe')).paddingBottom);
      return {above:dot.top-buttons.bottom,below:innerHeight-inset-dot.bottom};''')
    assert report['verticalSpacing']=={'above':16,'below':16},report['verticalSpacing']
    goto(4,'#finish-page.visible')
    assert all(d['filled'] for d in dots())
    after=prefs()
    assert after['services.user_consented']==before['services.user_consented']==False
    assert after['completed_onboarding']==before['completed_onboarding']==False
    report['jumpDoesNotConsentOrFinish']=True
    goto(2,'#search-engines-page.visible')
    js("[...document.querySelectorAll('#search-engines-page button')].find(b=>b.innerText.startsWith('DuckDuckGo')).click()")
    wait("return document.querySelector('#search-engines-page button[aria-pressed=true]')?.innerText.startsWith('DuckDuckGo')")
    goto(1,'#services-page.visible')
    js("document.querySelector('#services-page button[role=switch]').click()")
    wait("return document.querySelectorAll('.progress-step').length===6")
    report['optionalStepDots']=dots()
    goto(5,'#finish-page.visible')
    goto(2,'#search-engines-page.visible')
    assert js("return document.querySelector('#search-engines-page button[aria-pressed=true]').innerText").startswith('DuckDuckGo')
    goto(0,'#welcome-page.visible')
    assert dots()[0]['current']=='step' and js("return document.querySelector('#setup-buttons')===null")
    goto(2,'#search-engines-page.visible')
    assert js("return document.querySelector('#search-engines-page button[aria-pressed=true]').innerText").startswith('DuckDuckGo')
    report['welcomeJumpPreservesChoices']=True
    report['jumpPreservesChoices']=True
    goto(1,'#services-page.visible')
    js("document.querySelector('#services-page button[role=switch]').click()")
    wait("return document.querySelectorAll('.progress-step').length===5")
    report['optionalStepRemoved']=True
    js("document.querySelectorAll('.progress-step')[1].focus()")
    wd('POST',prefix+'/actions',{'actions':[{'type':'key','id':'keyboard','actions':[
        {'type':'keyDown','value':'\ue004'},{'type':'keyUp','value':'\ue004'},
        {'type':'keyDown','value':'\ue007'},{'type':'keyUp','value':'\ue007'}]}]})
    wait("return !!document.querySelector('#search-engines-page.visible')")
    assert dots()[2]['current']=='step'
    report['keyboardNavigation']=True
    for width,height in [(900,650),(1200,850)]:
        wd('POST',prefix+'/window/rect',{'width':width,'height':height})
        time.sleep(.5)
        value=geometry()
        assert abs(value['footerBottom']-value['bottom']-10)<1,value
        assert value['footerTop']>0,value
        report[f'window{width}x{height}']=value
    wd('POST',prefix+'/window/rect',{'width':1100,'height':800})
    time.sleep(.5)
    report['previewGeometry']=geometry()
    report['fadeClearance']=js("""const scroller=document.querySelector('#search-engines-page .scrollable-page');
      scroller.scrollTop=scroller.scrollHeight;
      const fade=document.querySelector('#setup-footer-fade').getBoundingClientRect();
      const buttons=document.querySelector('#setup-buttons').getBoundingClientRect();
      const content=scroller.querySelector('.page-content').getBoundingClientRect();
      return {aboveButtons:buttons.top-fade.top,contentClearance:fade.top-content.bottom,
        mask:getComputedStyle(scroller).maskImage,scrollTop:scroller.scrollTop,
        maxScroll:scroller.scrollHeight-scroller.clientHeight,fadeBottom:innerHeight-fade.bottom};""")
    assert report['fadeClearance']['aboveButtons']==12,report['fadeClearance']
    assert report['fadeClearance']['contentClearance']>=0,report['fadeClearance']
    assert report['fadeClearance']['mask']=='none',report['fadeClearance']
    assert report['fadeClearance']['fadeBottom']==0,report['fadeClearance']
    # Exercise a new renderer/document while the same native alert stack stays.
    fixture='<meta name="viewport" content="width=device-width"><title>Safe area probe</title><p>Safe area probe</p>'
    wd('POST',prefix+'/url',{'url':'data:text/html,'+quote(fixture)})
    wait("return document.title==='Safe area probe'")
    time.sleep(.3)
    assert geometry()['bottom']==0,geometry()
    js("document.querySelector('meta[name=viewport]').content='width=device-width,viewport-fit=cover'")
    for _ in range(100):
        if geometry()['bottom']>0: break
        time.sleep(.1)
    report['newDocumentCover']=geometry()
    assert report['newDocumentCover']['bottom']>0,report['newDocumentCover']
    js("document.querySelector('meta[name=viewport]').content='width=device-width,viewport-fit=contain'")
    for _ in range(100):
        if geometry()['bottom']==0: break
        time.sleep(.1)
    assert geometry()['bottom']==0,geometry()
    report['dynamicViewportFit']=True
    wd('POST',prefix+'/url',{'url':'chrome://setup/'})
    wait("return !!document.querySelector('.welcome-actions .primary')")
    js("document.querySelector('.welcome-actions .primary').click()")
    wait("return !!document.querySelector('#services-page.visible')")
    goto(2,'#search-engines-page.visible')
    time.sleep(.8)
    report['returnedToSetup']=geometry()
    assert report['returnedToSetup']['bottom']>0,report['returnedToSetup']
    screenshot('setup-progress')
    report['pass']=True
finally:
    (evidence/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    try:
        wd('DELETE',prefix)
    finally:
        driver.terminate()
        driver.wait(timeout=10)
        log.close()
print(json.dumps(report,indent=2),flush=True)
