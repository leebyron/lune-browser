#!/usr/bin/env python3
"""Exercise actual renderer pixels and input, with and without the opt-in flag.

Requires Pillow. Uses only disposable profiles, a local fixture and ChromeDriver.
"""
import argparse
import base64
import io
import json
import socket
import subprocess
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, ProxyHandler, build_opener
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('output', type=Path)
parser.add_argument('evidence', type=Path)
parser.add_argument('--headed', action='store_true')
parser.add_argument('--observe', action='store_true')
parser.add_argument('--classic', action='store_true', help='Isolate renderer checks from native floating UI')
args = parser.parse_args()
out, evidence = args.output.resolve(), args.evidence.resolve()
evidence.mkdir(parents=True, exist_ok=True)
with socket.socket() as sock:
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
opener = build_opener(ProxyHandler({}))

def request(method, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    try:
        with opener.open(Request(f'http://127.0.0.1:{port}' + path, data=data,
                                 method=method, headers={'Content-Type':'application/json'}), timeout=90) as response:
            value = json.load(response)['value']
    except HTTPError as error:
        raise RuntimeError(error.read().decode()) from error
    if isinstance(value, dict) and 'error' in value:
        raise RuntimeError(value)
    return value

log = (evidence/'chromedriver.log').open('w')
driver = subprocess.Popen([str(out/'chromedriver'), f'--port={port}',
                           '--allowed-ips=127.0.0.1'], stdout=log, stderr=subprocess.STDOUT)
report = {}
try:
    for _ in range(100):
        try:
            if request('GET','/status')['ready']:
                break
        except OSError:
            time.sleep(.1)
    for enabled in (False, True):
        label = 'inset' if enabled else 'baseline'
        profile = evidence / (label+'-profile')
        assert not profile.exists(), f'Use a fresh evidence directory: {profile}'
        launch_args = ['--disable-background-networking', '--use-mock-keychain', '--force-color-profile=srgb',
                       '--password-store=basic', '--window-size=1200,900',
                       f'--user-data-dir={profile}']
        if not args.headed:
            launch_args += ['--headless=new']
        if enabled:
            launch_args += ['--lune-obscured-header-prototype']
        session = request('POST','/session',{'capabilities':{'alwaysMatch':{
            'goog:chromeOptions': {'binary':str(out/'Lune.app/Contents/MacOS/Lune'),
                                  'excludeSwitches':['enable-automation'],
                                  'args':launch_args,
                                  'prefs':{'helium.services.enabled':False,
                                           'helium.services.browser_updates':False,
                                           'helium.browser.layout':0 if args.classic else 2,
                                           'helium.browser.zen_mode_top_chrome_pinned':False}}}}})
        sid = '/session/'+session['sessionId']
        def js(script):
            return request('POST',sid+'/execute/sync',{'script':script,'args':[]})
        def cdp(cmd, params=None):
            return request('POST',sid+'/goog/cdp/execute',{'cmd':cmd,'params':params or {}})
        def screenshot(name):
            png = base64.b64decode(cdp('Page.captureScreenshot',{'captureBeyondViewport':False})['data'])
            (evidence/f'{label}-{name}.png').write_bytes(png)
            return Image.open(io.BytesIO(png)).convert('RGB')
        try:
            request('POST',sid+'/url',{'url':Path(__file__).with_name('page.html').resolve().as_uri()})
            time.sleep(.5)
            metrics = js('''return {height:innerHeight, width:innerWidth, dpr:devicePixelRatio,
              visualHeight:visualViewport.height, clientHeight:document.documentElement.clientHeight,
              fixed:document.querySelector('#fixed').getBoundingClientRect().toJSON(),
              origin:document.querySelector('#origin').getBoundingClientRect().toJSON()};''')
            samples = []
            for scroll in (0,26,52,160):
                js(f'window.scrollTo(0,{scroll})')
                time.sleep(.15)
                image = screenshot(f'scroll-{scroll}')
                scale = image.width/metrics['width']
                colors = [image.getpixel((round(8*scale),round(y*scale))) for y in (8,28,54,80)]
                samples.append({'scroll':js('return scrollY'), 'image':image.size,
                                'colors':colors, 'scale':scale})
            js('window.scrollTo(0,0)')
            time.sleep(.15)
            rect = js("return document.querySelector('#fixed').getBoundingClientRect().toJSON()")
            x = rect['x']+rect['width']/2
            y = rect['y']+rect['height']/2+(52 if enabled else 0)
            for kind in ('mousePressed','mouseReleased'):
                cdp('Input.dispatchMouseEvent',{'type':kind,'x':x,'y':y,'button':'left','clickCount':1})
            clicks = js('return window.clicks')
            js("document.documentElement.style.background='#654322'")
            time.sleep(.15)
            image = screenshot('background-changed')
            changed_color = image.getpixel((round(8*scale),round(28*scale)))
            js("document.documentElement.style.background='transparent'; document.body.style.background='#123456'")
            time.sleep(.15)
            image = screenshot('body-background')
            body_color = image.getpixel((round(8*scale),round(28*scale)))
            js("""document.body.style.background='transparent';
                document.documentElement.style.background='linear-gradient(90deg,#123456 0 50%,#abcdef 50% 100%)'""")
            time.sleep(.15)
            image = screenshot('background-image')
            background_image = [image.getpixel((round(x*scale),round(28*scale)))
                                for x in (8,metrics['width']-8)]
            js("document.documentElement.style.background='#244634'")
            js("document.querySelector('#target').scrollIntoView()")
            time.sleep(.15)
            target = js("return document.querySelector('#target').getBoundingClientRect().toJSON()")
            screenshot('anchor')
            js("""window.originClicks=0; document.querySelector('#origin').onclick=()=>window.originClicks++;
                window.lastClick=null; document.addEventListener('click',event=>{
                  window.lastClick={target:event.target.id, y:event.clientY, pageY:event.pageY};
                });""")
            js('window.scrollTo(0,52)')
            time.sleep(.15)
            for kind in ('mousePressed','mouseReleased'):
                cdp('Input.dispatchMouseEvent',{'type':kind,'x':600,'y':28,'button':'left','clickCount':1})
            origin_clicks = js('return window.originClicks')
            strip_click = js('return window.lastClick')
            cdp('Performance.enable')
            def perf():
                return {m['name']:m['value'] for m in cdp('Performance.getMetrics')['metrics']
                        if m['name'] in ('LayoutCount','RecalcStyleCount','LayoutDuration')}
            before = perf()
            cdp('Input.dispatchMouseEvent',{'type':'mouseWheel','x':600,'y':28,'deltaX':0,'deltaY':80})
            time.sleep(.6)
            wheel_scroll = js('return scrollY')
            after = perf()
            js("document.querySelector('#nested').style.top='-30px'")
            time.sleep(.15)
            cdp('Input.dispatchMouseEvent',{'type':'mouseWheel','x':metrics['width']-100,
                                          'y':28,'deltaX':0,'deltaY':80})
            time.sleep(.6)
            nested_scroll = js("return document.querySelector('#nested').scrollTop")
            report[label] = {'metrics':metrics,'samples':samples,'clicks':clicks,
                             'changed_color':changed_color,'anchor':target,
                             'body_color':body_color,'background_image':background_image,
                             'background_image_supported':background_image==[(18,52,86),(171,205,239)],
                             'origin_clicks':origin_clicks,'wheel_scroll':wheel_scroll,
                             'strip_click':strip_click,
                             'nested_scroll':nested_scroll,
                             'scroll_performance_delta':{k:after[k]-v for k,v in before.items()}}
            print(label, json.dumps(report[label]), flush=True)
            (evidence/'results.json').write_text(json.dumps(report,indent=2)+'\n')
        finally:
            request('DELETE',sid)
    (evidence/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    if not args.observe:
        assert report['baseline']['clicks']==1
        assert report['inset']['clicks']==1
        assert report['baseline']['metrics']['height']-report['inset']['metrics']['height']==52
        assert tuple(report['inset']['samples'][0]['colors'][0])==(36,70,52)
        assert tuple(report['inset']['samples'][2]['colors'][1])==(224,69,69)
        assert tuple(report['inset']['changed_color'])==(101,67,34)
        assert tuple(report['inset']['body_color'])==(18,52,86)
        # Image extension is a capability probe, beyond this color-only prototype.
        assert report['inset']['origin_clicks']==1
        assert report['inset']['wheel_scroll']>52
        assert report['inset']['nested_scroll']>0
        assert report['inset']['scroll_performance_delta']['LayoutCount']==0
        print('PASS: inset, scroll-under pixels, background changes and input alignment')
        print('Root background-image extension:', report['inset']['background_image_supported'])
finally:
    driver.terminate()
    driver.wait(timeout=20)
    log.close()
