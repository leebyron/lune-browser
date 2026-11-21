"""Exercise the pinned toolbar's renderer contract through packaged Settings."""
import json
import math
import time


MODES = {
    'hover': (False, False, False),
    'no-hover': (False, False, True),
    'always': (True, False, False),
    'cover': (True, True, False),
}
PREFS = (
    'helium.browser.zen_mode_top_chrome_pinned',
    'helium.browser.top_controls_overlay',
    'helium.browser.top_controls_hover_disabled',
)
ZOOMS = (1, .8, 1.25)
HEIGHTS = ('inner', 'visual', 'client', 'vh', 'dvh')
INSET_PT = 52
# innerHeight and clientHeight are integer CSS values rounded at both samples.
POINT_TOLERANCE = 1.5
METRICS = '''
const rect = id => document.querySelector(id).getBoundingClientRect();
return {
  inner: innerHeight, visual: visualViewport.height,
  client: document.documentElement.clientHeight,
  vh: rect('#vh').height, dvh: rect('#dvh').height,
  safe: parseFloat(getComputedStyle(document.querySelector('#safe')).paddingTop),
  fixed: rect('#fixed').top, sticky: rect('#sticky').top,
  dpr: devicePixelRatio, outer: outerHeight, scroll: scrollY, marker: window.toolbarInsetMarker,
};
'''


def check_toolbar_inset(request, path, fixture_url, find_js, report, phase, display_scale):
    """Append measurements and assertion failures to the artifact's smoke report."""
    failures = report.setdefault('failures', [])
    cases = report.setdefault('cases', [])

    def command(method, endpoint, data=None):
        return request(method, path + endpoint, data)

    def js(script, *args, async_=False):
        return command('POST', '/execute/' + ('async' if async_ else 'sync'),
                       {'script': script, 'args': args})

    def converge(read, condition, label):
        for _ in range(60):
            value = read()
            if condition(value):
                return value
            time.sleep(.1)
        raise AssertionError(f'{label} did not settle. Last value {value!r}')

    def activate(handle):
        command('POST', '/window', {'handle': handle})

    def page(kind, new_type):
        handle = command('POST', '/window/new', {'type': new_type})['handle']
        activate(handle)
        url = fixture_url + ('?cover' if kind == 'cover' else '')

        def navigate():
            # First-run initialization can replace a navigation with New Tab.
            command('POST', '/url', {'url': url})
            return js('return [location.href, document.title, typeof window.trustedClicks];')

        converge(navigate,
                 lambda value: value == [url, 'Lune toolbar inset fixture', 'number'],
                 f'{kind} fixture navigation')
        js('window.toolbarInsetMarker = arguments[0];', kind)
        return handle

    def wait_for_mode(expected):
        def state():
            return js(find_js + '''
              const done = arguments[arguments.length - 1];
              Promise.all(arguments[0].map(k => chrome.settingsPrivate.getPref(k)))
                .then(prefs => done([find('#showToolbar').getSelectedValue(),
                                    ...prefs.map(p => p.value)]));
            ''', PREFS, async_=True)
        return converge(state, lambda value: value == [expected, *MODES[expected]],
                        f'Settings mode {expected}')

    def set_mode(expected):
        activate(settings)
        js(find_js + '''
          const select = find('#showToolbar').shadowRoot.querySelector('select');
          select.value = arguments[0];
          select.dispatchEvent(new Event('change'));
        ''', expected)
        wait_for_mode(expected)

    def set_zoom(zoom):
        activate(settings)
        js(find_js + '''
          const select = find('#zoomLevel');
          select.value = String(arguments[0]);
          select.dispatchEvent(new Event('change'));
        ''', zoom)
        converge(lambda: js('chrome.settingsPrivate.getDefaultZoom().then(arguments[0]);',
                            async_=True),
                 lambda value: abs(value - zoom) < .001, f'Settings zoom {zoom}')

    def measure(kind, handle, zoom):
        activate(handle)
        converge(lambda: js('return devicePixelRatio;'),
                 lambda dpr: abs(dpr - scale * zoom) < .01, f'{kind} page zoom {zoom}')
        js('const done = arguments[0]; requestAnimationFrame(() => requestAnimationFrame(done));',
           async_=True)
        return js(METRICS)

    def check(case, field, actual, expected, tolerance=0):
        matched = (math.isclose(actual, expected, abs_tol=tolerance) if tolerance
                   else actual == expected)
        if not matched:
            failures.append({**case, 'field': field, 'actual': actual, 'expected': expected})

    def geometry(case, metrics, baseline, inset, safe):
        cases.append({**case, 'metrics': metrics})
        check(case, 'document marker', metrics['marker'], case['page'])
        zoom = case['zoom']
        for field in HEIGHTS:
            check(case, f'{field} inset (pt)', (baseline[field] - metrics[field]) * zoom,
                  inset, POINT_TOLERANCE)
        check(case, 'safe area (pt)', metrics['safe'] * zoom, safe, POINT_TOLERANCE)
        check(case, 'fixed top (CSS px)', metrics['fixed'], 0, .1)
        check(case, 'retained scroll (CSS px)', metrics['scroll'], baseline['scroll'], 1)

    def cdp(name, **params):
        return command('POST', '/goog/cdp/execute', {'cmd': name, 'params': params})

    def pointer(target, action, inset):
        point = js('''
          const rect = document.querySelector(arguments[0]).getBoundingClientRect();
          return {x: rect.x + rect.width / 2, y: rect.y + rect.height / 2};
        ''', target)
        point['y'] += inset
        if action == 'wheel':
            cdp('Input.dispatchMouseEvent', type='mouseWheel', deltaX=0, deltaY=160, **point)
        else:
            for event in ('mousePressed', 'mouseReleased'):
                cdp('Input.dispatchMouseEvent', type=event, button='left', clickCount=1, **point)

    def check_input(page_handle, kind, mode, zoom, inset):
        activate(page_handle)
        js("""
          scrollTo(0, 0);
          document.querySelector('#nested').scrollTop = 0;
          document.querySelector('#field').value = '';
        """)
        case = {'phase': phase, 'page': kind, 'mode': mode, 'zoom': zoom, 'scenario': 'input'}
        count = js('return trustedClicks;')
        pointer('#click', 'click', inset)
        check(case, 'trusted fixed button click', js('return trustedClicks;'), count + 1)
        pointer('#nested', 'wheel', inset)
        nested = converge(lambda: js("return document.querySelector('#nested').scrollTop;"),
                          lambda value: value > 0, f'{kind} {mode} nested wheel')
        check(case, 'nested wheel leaves page scroll', js('return scrollY;'), 0)
        pointer('#fixed', 'wheel', inset)
        page_scroll = converge(lambda: js('return scrollY;'), lambda value: value > 60,
                               f'{kind} {mode} page wheel')
        after_scroll = js(METRICS)
        check(case, 'sticky top after scrolling (CSS px)', after_scroll['sticky'], 36, 1)
        pointer('#fixed a', 'click', inset)
        anchor = js("return {hash: location.hash, top: document.querySelector('#target').getBoundingClientRect().top};")
        check(case, 'anchor fragment', anchor['hash'], '#target')
        check(case, 'anchor scroll margin', anchor['top'], 110, 1)
        pointer('#field', 'click', inset)
        cdp('Input.insertText', text='Lune')
        field = js("return {focus: document.activeElement.id, value: document.querySelector('#field').value};")
        check(case, 'form focus and text input', field, {'focus': 'field', 'value': 'Lune'})
        cases.append({**case, 'nested_scroll': nested, 'page_scroll': page_scroll,
                      'anchor': anchor, 'field': field})
        js("history.replaceState(null, '', location.pathname + location.search);")

    def check_fullscreen(kind, handle, mode):
        before = measure(kind, handle, 1)
        result = cdp('Runtime.evaluate', expression='document.documentElement.requestFullscreen()',
                     userGesture=True, awaitPromise=True)
        if 'exceptionDetails' in result:
            raise AssertionError(f'{kind} fullscreen request failed: {result["exceptionDetails"]}')
        converge(lambda: js('return !!document.fullscreenElement;'), bool, f'{kind} fullscreen')
        fullscreen = measure(kind, handle, 1)
        case = {'phase': phase, 'page': kind, 'mode': mode, 'zoom': 1, 'scenario': 'DOM fullscreen'}
        for field in HEIGHTS:
            check(case, f'fullscreen {field} height', fullscreen[field], fullscreen['outer'], 1)
        check(case, 'fullscreen safe area', fullscreen['safe'], 0)
        js('document.exitFullscreen().then(arguments[0]);', async_=True)
        converge(lambda: js('return !document.fullscreenElement;'), bool, f'{kind} fullscreen exit')
        restored = measure(kind, handle, 1)
        for field in (*HEIGHTS, 'safe'):
            check(case, f'restored {field}', restored[field], before[field], 1)
        cases.append({**case, 'before': before, 'fullscreen': fullscreen, 'restored': restored})

    settings = command('GET', '/window')
    command('POST', '/url', {'url': 'chrome://settings/appearance'})
    converge(lambda: js(find_js + "return !!find('#showToolbar')?.getSelectedValue();"),
             bool, 'Show toolbar Settings control')
    wait_for_mode('hover' if phase == 'write' else 'cover')
    pages = {
        'ordinary': page('ordinary', 'tab'),
        'cover': page('cover', 'window' if phase == 'write' else 'tab'),
    }
    activate(pages['ordinary'])
    scale = display_scale or js('return devicePixelRatio;')
    report['display_scale'] = scale

    if phase == 'read':
        restored = {kind: measure(kind, handle, 1) for kind, handle in pages.items()}
        check_fullscreen('cover', pages['cover'], 'cover')
        set_mode('hover')
        for kind, handle in pages.items():
            baseline = measure(kind, handle, 1)
            geometry({'phase': phase, 'page': kind, 'mode': 'cover', 'zoom': 1},
                     restored[kind], baseline,
                     INSET_PT if kind == 'ordinary' else 0,
                     INSET_PT if kind == 'cover' else 0)
        if failures:
            raise AssertionError(f'{len(failures)} toolbar inset checks failed. First: '
                                 + json.dumps(failures[0]))
        report['passed'] = True
        return

    for zoom in ZOOMS:
        set_zoom(zoom)
        set_mode('hover')
        baseline = {}
        for kind, handle in pages.items():
            activate(handle)
            js('scrollTo(0, 180);')
            baseline[kind] = measure(kind, handle, zoom)
        for mode in MODES:
            if mode != 'hover':
                set_mode(mode)
            for kind, handle in pages.items():
                metrics = measure(kind, handle, zoom)
                case = {'phase': phase, 'page': kind, 'mode': mode, 'zoom': zoom}
                overlays = mode == 'cover' and kind == 'cover'
                geometry(case, metrics, baseline[kind],
                         INSET_PT if MODES[mode][0] and not overlays else 0,
                         INSET_PT if overlays else 0)
                if (mode == 'always' and kind == 'ordinary') or overlays:
                    check_input(handle, kind, mode, zoom, 0 if overlays else INSET_PT / zoom)
                    js('scrollTo(0, 180);')
                if overlays:
                    for fit, inset, safe in (('contain', INSET_PT, 0), ('cover', 0, INSET_PT)):
                        js("document.querySelector('meta[name=viewport]').content = 'viewport-fit=' + arguments[0];", fit)
                        geometry({**case, 'viewport_fit': fit}, measure(kind, handle, zoom),
                                 baseline[kind], inset, safe)
    set_zoom(1)
    set_mode('always')
    check_fullscreen('ordinary', pages['ordinary'], 'always')
    set_mode('cover')
