// Loaded by preview-setup.mjs before the real setup app mounts.
import '/src/lib/chrome-send-polyfill.ts';
import { currentPage, flow, goToPage } from '/src/lib/onboarding-flow.ts';
import { uBlockOriginId, WebstoreInstallErrorCode } from '/src/lib/browser/index.ts';
import {
    ImportDataStatus, sendWithPromise, webUIListenerCallback, webUIResponse,
} from '/src/lib/cr/index.ts';

const url = new URL(location.href);
const scenario = url.searchParams.get('scenario') ?? 'fresh';
const scenarios = ['fresh', 'services-off', 'import-empty', 'import-error', 'import-failure', 'extension-error'];
const step = url.searchParams.get('step') ?? flow[0];
if (!scenarios.includes(scenario) || !flow.includes(step)) {
    throw new Error(`Unknown setup preview step or scenario. Steps: ${flow.join(', ')}. Scenarios: ${scenarios.join(', ')}.`);
}

const send = chrome.send.bind(chrome);
const prefs = {
    'search.suggest_enabled': true,
    ...await sendWithPromise('getPrefs'),
};
if (scenario === 'services-off') {
    prefs['services.enabled'] = false;
    prefs['services.user_consented'] = true;
}

// Initialize the mock's selection from its advertised default before changing engines.
const engines = await sendWithPromise('getSearchEnginesList');
const defaultEngine = engines.defaults.find(engine => engine.default);
if (defaultEngine) send('setDefaultSearchEngine', [defaultEngine.id]);

let blockerEnabled;
chrome.send = (message, args = []) => {
    const [id, key, value] = args;
    switch (message) {
        case 'getPrefs':
            webUIResponse(id, true, { ...prefs });
            return;
        case 'setPref':
            if (!Object.hasOwn(prefs, key) || typeof prefs[key] !== typeof value) {
                webUIResponse(id, false, `Invalid setup preference: ${key}`);
                return;
            }
            prefs[key] = value;
            webUIResponse(id, true, null);
            webUIListenerCallback('helium-prefs-changed', { ...prefs });
            return;
        case 'setUBlockEnabled':
            prefs['ublock.enabled'] = key;
            if (key) prefs['ublock.install_allowed'] = true;
            if (key || blockerEnabled !== undefined) {
                blockerEnabled = key;
                webUIListenerCallback('extension-state-changed', { [uBlockOriginId]: key });
            }
            webUIListenerCallback('helium-prefs-changed', { ...prefs });
            webUIResponse(id, true, key);
            return;
        case 'initializeImportDialog':
            if (scenario === 'import-empty' || scenario === 'import-error') {
                setTimeout(() => webUIResponse(id, scenario === 'import-empty', []), 250);
                return;
            }
            break;
        case 'importData':
        case 'importFromBookmarksFile': {
            const status = scenario === 'import-failure' ? ImportDataStatus.FAILED : ImportDataStatus.SUCCEEDED;
            webUIListenerCallback('import-data-status-changed', ImportDataStatus.IN_PROGRESS);
            setTimeout(() => webUIListenerCallback('import-data-status-changed', status), 500);
            return;
        }
        case 'installExtension':
            if (scenario === 'extension-error') {
                setTimeout(() => webUIResponse(id, false, {
                    code: WebstoreInstallErrorCode.WebstoreRequestError,
                    error: 'Simulated extension download failure',
                }), 250);
                return;
            }
            break;
    }
    send(message, args);
};

// Allow Vite's full reloads after the user has interacted with setup.
window.addEventListener('beforeunload', event => event.stopImmediatePropagation(), { capture: true });

// Simulate new-tab completion within the HTTP preview.
const open = window.open.bind(window);
window.open = (target, name, features) => {
    if (name === '_self' && /^chrome(?:-native)?:\/\/newtab\/?$/.test(target)) {
        const notice = document.createElement('p');
        notice.id = 'setup-preview-complete';
        notice.setAttribute('role', 'status');
        notice.textContent = 'Setup complete. Reload to reset the preview.';
        notice.style.cssText = 'position:fixed;inset:12px 12px auto auto;z-index:20;margin:0;padding:8px 12px;background:Canvas;color:CanvasText;border-radius:8px';
        document.querySelector('#setup-preview-complete')?.remove();
        document.body.append(notice);
        return null;
    }
    return open(target, name, features);
};

goToPage(step);
currentPage.subscribe(page => {
    // Keep the active step after a Vite full reload, including string edits.
    const currentUrl = new URL(location.href);
    if (page === flow[0]) currentUrl.searchParams.delete('step');
    else currentUrl.searchParams.set('step', page);
    if (currentUrl.href !== location.href) history.replaceState(history.state, '', currentUrl);
});
