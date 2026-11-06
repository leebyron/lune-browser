"""Opt-in live Helium service checks in a disposable browser test profile."""
import json
import re
import time


def parse_bangs(text):
    # The native loader permits comments and trailing commas. Match strings
    # first so URL slashes and punctuation inside quoted values stay untouched.
    tokens = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/', re.DOTALL)
    text = tokens.sub(lambda m: m[0] if m[0].startswith('"') else ' ', text)
    tokens = re.compile(r'"(?:\\.|[^"\\])*"|,(?=\s*[}\]])', re.DOTALL)
    return json.loads(tokens.sub(lambda m: m[0] if m[0].startswith('"') else '', text))


def check_services(request, path, fixture_url):
    def js(code, asynchronous=False, args=None):
        return request('POST', path + '/execute/' + ('async' if asynchronous else 'sync'),
                       {'script': code, 'args': args or []})

    request('POST', path + '/url', {'url': 'chrome://settings/privacy/services'})
    for key, value in [('helium.services.browser_updates', False),
                       ('helium.services.enabled', True),
                       ('helium.services.user_consented', True)]:
        result = js('const done=arguments[arguments.length-1]; chrome.settingsPrivate.setPref(arguments[0],arguments[1],"",done);',
                    True, [key, value])
        if result is not True:
            raise RuntimeError('Cannot enable disposable-profile service consent: ' + key)
    # Component uBlock is present without a Web Store install or user account.
    request('POST', path + '/url', {'url': 'chrome-extension://blockjmkbacgjkknlgpkjjiijinjdanf/3p-filters.html'})
    for attempt in range(120):
        if js('return typeof vAPI !== "undefined";'):
            break
        if attempt % 10 == 9:
            request('POST', path + '/url', {'url': 'chrome-extension://blockjmkbacgjkknlgpkjjiijinjdanf/3p-filters.html'})
        time.sleep(0.5)
    else:
        raise RuntimeError('Bundled uBlock dashboard did not initialize')
    lists = js('const done=arguments[arguments.length-1]; vAPI.messaging.send("dashboard",{what:"getLists"}).then(done);', True)
    if not lists or lists.get('netFilterCount', 0) < 1000:
        raise RuntimeError('Bundled uBlock network filters did not load')
    bangs = js('''const done=arguments[arguments.length-1];
      fetch('https://services.helium.imput.net/bangs.json')
        .then(async r => done({status:r.status,text:await r.text()}))
        .catch(e => done({error:String(e)}));''', True)
    if bangs.get('status') == 200:
        data = parse_bangs(bangs.pop('text'))
        bangs['entries'] = len(data) if isinstance(data, list) else 0
        bangs['valid_entries'] = sum(isinstance(row, dict) and bool(row.get('s'))
                                    and isinstance(row.get('ts'), list)
                                    and str(row.get('u', '')).startswith(('https://', 'http://'))
                                    for row in data)
    if bangs.get('status') != 200 or bangs.get('entries', 0) < 100:
        raise RuntimeError('Helium bangs endpoint failed: ' + json.dumps(bangs))
    js('vAPI.messaging.send("dashboard",{what:"updateNow"}); return true;')
    time.sleep(5)
    # A component update can reload the dashboard during the live check.
    request('POST', path + '/url', {'url': 'chrome-extension://blockjmkbacgjkknlgpkjjiijinjdanf/3p-filters.html'})
    for _ in range(60):
        if js('return typeof vAPI !== "undefined";'):
            break
        time.sleep(0.5)
    updated = js('const done=arguments[arguments.length-1]; vAPI.messaging.send("dashboard",{what:"getLists"}).then(done);', True)
    request('POST', path + '/url', {'url': fixture_url})
    request('POST', path + '/goog/cdp/execute', {'cmd': 'Network.enable', 'params': {}})
    js('''const script=document.createElement('script');
       script.src='https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js';
       document.body.appendChild(script); return true;''')
    time.sleep(2)
    logs = request('POST', path + '/log', {'type': 'performance'})
    messages = [json.loads(entry['message'])['message'] for entry in logs]
    ids = {m['params']['requestId'] for m in messages if m['method'] == 'Network.requestWillBeSent'
           and 'pagead2.googlesyndication.com' in m['params']['request']['url']}
    blocked = [m['params'] for m in messages if m['method'] == 'Network.loadingFailed'
               and m['params']['requestId'] in ids and m['params'].get('errorText') == 'net::ERR_BLOCKED_BY_CLIENT']
    redirects = [m['params'] for m in messages if m['method'] == 'Network.requestWillBeSent'
                 and m['params']['requestId'] in ids
                 and m['params']['request']['url'].startswith(
                     'chrome-extension://blockjmkbacgjkknlgpkjjiijinjdanf/web_accessible_resources/googlesyndication_adsbygoogle.js?')
                 and m['params'].get('redirectResponse', {}).get('headers', {}).get('Non-Authoritative-Reason') == 'WebRequest API']
    if not blocked and not redirects:
        diagnostics = [m for m in messages if m.get('params', {}).get('requestId') in ids]
        raise RuntimeError('uBlock did not block the known advertising fixture: ' + json.dumps(diagnostics))
    return {'provider': 'Helium', 'bangs': bangs, 'ublock_network_filters': lists['netFilterCount'],
            'ublock_update_requested': True, 'ublock_cache_entries': len(updated.get('cache') or {}),
            'advertising_fixture_blocked': True, 'profile': 'disposable; consent explicitly enabled',
            'advertising_action': 'local uBlock replacement' if redirects else 'blocked by client',
            'extension_install_update_tested': False}
