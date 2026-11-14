#!/usr/bin/env python3
"""Exercise Older tabs with a real saved session and an isolated local profile.

Run with BUILD_OUTPUT EVIDENCE_DIR. The default case takes about six minutes
because it observes the real launch grace and minute sweep. --interactive holds
the browser open until EVIDENCE_DIR/finish is created. --review gives seeded
Older tabs fresh retention clocks so a manual preview remains available.
--group-check instead runs a short expanded/collapsed group exclusion case.
--entry-clock-check verifies fixed entry-based retention through actual trusted
input, restart, active-tab protection, automatic closing and explicit recovery.
--startup-check tests a clean quit with Continue, New Tab, or specified pages;
it relaunches without a command-line page that could override startup policy.
Requires requests and the bundled build's ChromeDriver; never uses a personal
profile, a remote test page, or real Keychain credentials.
"""
from pathlib import Path
import argparse, base64, hashlib, http.server, json, socket, subprocess, threading, time
import requests
import struct
from older_tabs_session_fixture import seed, states

p = argparse.ArgumentParser()
p.add_argument("output", type=Path)
p.add_argument("evidence", type=Path)
p.add_argument("--interactive", action="store_true")
p.add_argument("--review", action="store_true")
p.add_argument(
    "--entry-clock-check",
    action="store_true",
    help="Verify activation/input/restart preserve the entry deadline and active-tab protection",
)
p.add_argument(
    "--arrangement-check",
    action="store_true",
    help="Check that real model reorders preserve inactivity while activation resets it",
)
p.add_argument(
    "--group-check",
    action="store_true",
    help="Check overdue grouped tabs against an ungrouped control, without waiting for closure",
)
p.add_argument(
    "--immediate-check",
    action="store_true",
    help="Verify direct historical closing without entering Older Tabs",
)
p.add_argument(
    "--move-grouped",
    action="store_true",
    help="Opt grouped tabs into the --group-check aging case",
)
p.add_argument(
    "--settings-check",
    action="store_true",
    help="Verify duration choices, group opt-in and Never collapse in WebUI",
)
p.add_argument(
    "--pinned-check",
    action="store_true",
    help="Verify inactive pinned tabs never age and stale Older state is cleared",
)
p.add_argument(
    "--startup-check",
    choices=["continue", "new-tab", "urls"],
    help="Verify Older tab residency across a clean quit with the selected startup mode",
)
p.add_argument(
    "--never-check",
    action="store_true",
    help="Verify Never disables cleanup across a clean session restore",
)
a = p.parse_args()
automatic_cases = [
    a.entry_clock_check,
    a.arrangement_check,
    a.settings_check,
    a.group_check,
    a.immediate_check,
    a.pinned_check,
    bool(a.startup_check),
    a.never_check,
]
if sum(automatic_cases) > 1 or (a.interactive and any(automatic_cases)):
    p.error("automatic check variants are mutually exclusive and cannot be interactive")
if a.move_grouped and not a.group_check:
    p.error("--move-grouped requires --group-check")
if a.review and not a.interactive:
    p.error("--review requires --interactive")
out = a.output.resolve()
ev = a.evidence.resolve()
ev.mkdir(parents=True, exist_ok=False)
profile = ev / "profile"
(profile / "Default").mkdir(parents=True)
(profile / "Default/Preferences").write_text(
    json.dumps(
        {
            "helium": {
                "completed_onboarding": True,
                "tabs": {
                    **({"cleanup_close_hours": -1} if a.immediate_check else {}),
                    **({"cleanup_move_grouped": True} if a.move_grouped else {}),
                },
                "services": {"enabled": False, "browser_updates": False},
            },
            "session": {"restore_on_startup": 1},
            "browser": {
                "window_placement": {
                    "left": 100,
                    "top": 100,
                    "right": 1300,
                    "bottom": 950,
                    "maximized": False,
                }
            },
        }
    )
)
# A public fixture key, generated in memory and used only to stabilize extension identity.
private = subprocess.run(
    ["/usr/bin/openssl", "genrsa", "2048"], capture_output=True, check=True
).stdout
key = subprocess.run(
    ["/usr/bin/openssl", "rsa", "-pubout", "-outform", "DER"],
    input=private,
    capture_output=True,
    check=True,
).stdout
del private
ident = "".join(
    chr(ord("a") + int(x, 16)) for x in hashlib.sha256(key).hexdigest()[:32]
)
ext = ev / "extension"
ext.mkdir()
(ext / "manifest.json").write_text(
    json.dumps(
        {
            "manifest_version": 3,
            "name": "Older tabs local fixture",
            "version": "1",
            "key": base64.b64encode(key).decode(),
            "permissions": ["tabs", "sessions", "tabGroups", "scripting"],
            "host_permissions": ["http://127.0.0.1/*"],
        }
    )
)
(ext / "fixture.html").write_text(
    "<!doctype html><title>Older tabs fixture</title><p>Local test controller</p>"
)


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        name = self.path.strip("/") or "A"
        title = {
            "A": "Today’s work",
            "B": "Release notes",
            "C": "Weekend reading",
            "D": "Project plan",
            "E": "Saved research",
            "F": "Design references",
            "G": "Protected draft",
        }.get(name, name)
        body = f'<!doctype html><meta charset="utf-8"><title>{title}</title><style>body{{font:18px system-ui;background:#f6f5f1;color:#343b41;margin:100px auto;max-width:640px;line-height:1.6}}h1{{font:48px Georgia}}small{{letter-spacing:.12em;font-size:12px;color:#66737a}}input,button{{font:inherit;padding:10px;border:1px solid #ddd;border-radius:8px;background:white}}</style><small>LUNE · LOCAL TEST PAGE</small><h1>{title}</h1><p>This isolated profile contains sample pages for reviewing Older tabs. Every page stays live as the sidebar organizes it.</p><input placeholder="Type here"><button onclick="window.onbeforeunload=()=>true">Protect this tab</button>'.encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
log = (ev / "driver.log").open("w")
driver = subprocess.Popen(
    [str(out / "chromedriver"), f"--port={port}", "--verbose"],
    stdout=log,
    stderr=subprocess.STDOUT,
)


def wd(method, path, data=None):
    v = requests.request(
        method,
        f"http://127.0.0.1:{port}" + path,
        json=data,
        timeout=180 if path == "/session" else 60,
    ).json()["value"]
    if isinstance(v, dict) and v.get("error"):
        raise RuntimeError(v)
    return v


sid = None
browser = None
dashboard = None
report = {}


def execute(script, *args):
    return wd("POST", sid + "/execute/sync", {"script": script, "args": list(args)})


def asyncjs(script, *args):
    return wd("POST", sid + "/execute/async", {"script": script, "args": list(args)})


def tabs():
    return asyncjs("chrome.tabs.query({}, arguments[arguments.length-1]);")


def launch(phase, startup_mode=None):
    global browser, sid, dashboard
    active = profile / "DevToolsActivePort"
    active.unlink(missing_ok=True)
    f = (ev / f"{phase}.log").open("w")
    browser = subprocess.Popen(
        [
            str(out / "Lune.app/Contents/MacOS/Lune"),
            *(
                ["--headless=new", "--window-size=1200,850"]
                if (
                    a.entry_clock_check
                    or a.group_check
                    or a.immediate_check
                    or a.settings_check
                    or a.pinned_check
                    or a.startup_check
                    or a.never_check
                    or a.arrangement_check
                )
                else []
            ),
            f"--user-data-dir={profile}",
            "--remote-debugging-port=0",
            "--use-mock-keychain",
            "--password-store=basic",
            "--disable-background-networking",
            "--disable-features=EncryptSessionStorage",
            f"--load-extension={ext}",
            f"--disable-extensions-except={ext}",
            "--custom-update-server-url=http://127.0.0.1:1/",
            "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1",
            *([] if startup_mode else [f"chrome-extension://{ident}/fixture.html"]),
        ],
        stdout=f,
        stderr=subprocess.STDOUT,
    )
    (ev / f"{phase}.pid").write_text(str(browser.pid) + "\n")
    for _ in range(600):
        if browser.poll() is not None:
            raise RuntimeError("Browser exited")
        if active.exists():
            break
        time.sleep(0.1)
    debug = int(active.read_text().splitlines()[0])
    for _ in range(300):
        if browser.poll() is not None:
            raise RuntimeError("Browser exited before opening a tab")
        targets = requests.get(f"http://127.0.0.1:{debug}/json/list", timeout=5).json()
        if any(x.get("type") == "page" for x in targets):
            break
        time.sleep(0.1)
    time.sleep(1)
    session = wd(
        "POST",
        "/session",
        {
            "capabilities": {
                "alwaysMatch": {
                    "goog:chromeOptions": {
                        "debuggerAddress": f"127.0.0.1:{debug}",
                        "enableExtensionTargets": True,
                    }
                }
            }
        },
    )
    sid = "/session/" + session["sessionId"]
    if startup_mode:
        # Observe real startup first. A command-line fixture URL would override
        # the configured startup pages, so create the test controller afterward.
        dump(
            "startup_targets",
            requests.get(f"http://127.0.0.1:{debug}/json/list", timeout=10).json(),
        )
        wd(
            "POST",
            sid + "/goog/cdp/execute",
            {
                "cmd": "Target.createTarget",
                "params": {"url": f"chrome-extension://{ident}/fixture.html"},
            },
        )
    # Resolve the fixture target through CDP without activating every saved tab.
    targets = requests.get(f"http://127.0.0.1:{debug}/json/list", timeout=10).json()
    target = next(
        x["id"]
        for x in targets
        if x.get("url", "").startswith(f"chrome-extension://{ident}")
    )
    handles = wd("GET", sid + "/window/handles")
    dashboard = next(h for h in handles if h.endswith(target))
    wd("POST", sid + "/window", {"handle": dashboard})
    wd("POST", sid + "/url", {"url": f"chrome-extension://{ident}/fixture.html"})
    print(
        "fixture context",
        execute(
            "return {url:location.href,tabs:!!chrome.tabs,body:document.body.innerText}"
        ),
        flush=True,
    )
    return debug


def quit_browser():
    global sid
    try:
        wd("POST", sid + "/goog/cdp/execute", {"cmd": "Browser.close", "params": {}})
    except Exception:
        pass
    browser.wait(timeout=30)
    assert browser.returncode == 0, browser.returncode
    try:
        wd("DELETE", sid)
    except Exception:
        pass
    sid = None


def dump(name, data):
    report[name] = data
    (ev / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    summary = data if isinstance(data, (bool, str, int, float)) else "recorded"
    if isinstance(data, list):
        summary = f"{len(data)} entries"
    print(f"{name}: {summary}", flush=True)


def check_arrangement(mapping):
    def saved_when(predicate):
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                saved = {state["id"]: state for state in states(profile).values()}
                if all(mapping[role] in saved for role in "AD") and predicate(saved):
                    return saved
            except (AssertionError, ValueError, IndexError, struct.error):
                # Session commands may be between writes; retry a complete read.
                pass
            time.sleep(0.2)
        raise AssertionError("Timed out waiting for saved arrangement state")

    clocks = ("id", "age", "last_use", "close_clock", "frozen")
    saved = saved_when(lambda value: all(mapping[role] in value for role in "AD"))
    before = {role: saved[mapping[role]].copy() for role in "AD"}
    assert all(before[role]["close_clock"] == "0" for role in "AD")
    live = {
        t["url"].rsplit("/", 1)[-1]: t
        for t in tabs()
        if t["url"].startswith("http:")
    }
    assert not live["A"]["active"] and not live["D"]["active"]

    moved = asyncjs(
        "chrome.tabs.move(arguments[0],{index:arguments[1]},arguments[arguments.length-1]);",
        live["A"]["id"],
        live["D"]["index"],
    )
    assert moved["index"] == live["D"]["index"], moved
    after = saved_when(
        lambda value: value[mapping["A"]]["order"] != before["A"]["order"]
    )
    for role in "AD":
        assert all(
            after[mapping[role]][key] == before[role][key] for key in clocks
        ), (role, before[role], after[mapping[role]])
    dump("reorder_preserves_clocks", True)

    # Arrange both tabs back together through the extension/model path.
    asyncjs(
        "chrome.tabs.move(arguments[0],{index:1},arguments[arguments.length-1]);",
        [live["A"]["id"], live["D"]["id"]],
    )
    previous_order = after[mapping["A"]]["order"]
    after = saved_when(lambda value: value[mapping["A"]]["order"] != previous_order)
    for role in "AD":
        assert all(
            after[mapping[role]][key] == before[role][key] for key in clocks
        ), (role, before[role], after[mapping[role]])
    dump("batch_reorder_preserves_clocks", True)

    asyncjs(
        "chrome.tabs.update(arguments[0],{active:true},arguments[arguments.length-1]);",
        live["A"]["id"],
    )
    after = saved_when(lambda value: value[mapping["A"]]["age"] != before["A"]["age"])
    assert after[mapping["A"]]["last_use"] != before["A"]["last_use"]
    assert after[mapping["A"]]["age"] == after[mapping["A"]]["last_use"]
    assert all(after[mapping["D"]][key] == before["D"][key] for key in clocks)
    dump("activation_resets_inactivity", True)
    dump("arrangement_passed", True)


def check_entry_clock(mapping):
    before = {v["id"]: v.copy() for v in states(profile).values()}
    older = next(t for t in tabs() if t["url"].endswith("/E"))
    targets = requests.get(
        f"http://127.0.0.1:{debug}/json/list", timeout=10
    ).json()
    target = next(t["id"] for t in targets if t.get("url", "").endswith("/E"))
    handle = next(h for h in wd("GET", sid + "/window/handles") if h.endswith(target))
    asyncjs(
        "chrome.tabs.update(arguments[0],{active:true},arguments[arguments.length-1]);",
        older["id"],
    )
    wd("POST", sid + "/window", {"handle": handle})
    execute("window.fixtureInput=[];for(const type of ['pointerdown','keydown','wheel'])document.addEventListener(type,e=>fixtureInput.push({type:e.type,trusted:e.isTrusted}),{passive:false});")
    element = wd("POST", sid + "/element", {"using": "css selector", "value": "input"})
    element_id = element["element-6066-11e4-a52e-4f735466cecf"]
    wd("POST", sid + f"/element/{element_id}/click", {})
    wd("POST", sid + f"/element/{element_id}/value", {"text": "deadline stays fixed"})
    wd("POST", sid + "/goog/cdp/execute", {"cmd": "Input.dispatchMouseEvent", "params": {
        "type": "mouseWheel", "x": 300, "y": 300, "deltaX": 0, "deltaY": 200,
    }})
    assert execute("return document.querySelector('input').value") == "deadline stays fixed"
    # Wheel dispatch crosses the compositor/main-thread boundary asynchronously.
    for _ in range(50):
        events = execute("return window.fixtureInput")
        if any(e["type"] == "wheel" for e in events):
            break
        time.sleep(0.1)
    assert all(any(e["type"] == kind and e["trusted"] for e in events)
               for kind in ("pointerdown", "keydown", "wheel")), events
    dump("trusted_input_events", events)
    quit_browser()
    after = {v["id"]: v for v in states(profile).values()}
    e = mapping["E"]
    assert after[e]["last_use"] != before[e]["last_use"], (before[e], after[e])
    for key in ("close_clock", "age", "frozen", "order"):
        assert after[e][key] == before[e][key], (key, before[e], after[e])
    dump("activation_and_trusted_input_preserve_entry", True)
    dump("before_restart", after[e])

    launch("entry-restart")
    older = next(t for t in tabs() if t["url"].endswith("/E"))
    asyncjs(
        "chrome.tabs.update(arguments[0],{active:true},arguments[arguments.length-1]);",
        older["id"],
    )
    # Keep the expired Older tab active beyond the unmodified five-minute launch
    # grace and minute sweep. The other overdue tab G proves cleanup is running.
    start = time.monotonic()
    while time.monotonic() - start < 330:
        if browser.poll() is not None:
            raise RuntimeError("Browser exited during entry deadline test")
        time.sleep(5)
    remaining = tabs()
    roles = {t["url"].rsplit("/", 1)[-1] for t in remaining}
    assert "E" in roles and "G" not in roles and "F" in roles, remaining
    assert next(t for t in remaining if t["id"] == older["id"])["active"]
    current = {v["id"]: v for v in states(profile).values()}
    assert current[e]["close_clock"] == before[e]["close_clock"]
    dump("restart_preserves_entry_and_active_tab_protection", True)
    control = next(t for t in remaining if t["url"].startswith("chrome-extension:"))
    asyncjs(
        "chrome.tabs.update(arguments[0],{active:true},arguments[arguments.length-1]);",
        control["id"],
    )
    deadline = time.monotonic() + 75
    while time.monotonic() < deadline:
        if not any(t["id"] == older["id"] for t in tabs()):
            break
        time.sleep(1)
    else:
        raise AssertionError("Expired Older tab survived after leaving it")
    recent = asyncjs("chrome.sessions.getRecentlyClosed({},arguments[arguments.length-1]);")
    assert all(any(x.get("tab", {}).get("url", "").endswith("/" + role) for x in recent)
               for role in "EG"), recent
    assert any(t["url"].endswith("/F") for t in tabs())
    dump("original_deadline_closes_after_leaving_tab", True)
    dump("recently_closed", recent)
    asyncjs(
        'const done=arguments[arguments.length-1];chrome.sessions.getRecentlyClosed({},items=>{const item=items.find(x=>x.tab&&x.tab.url.endsWith("/E"));chrome.sessions.restore(item.tab.sessionId,result=>done(result));});'
    )
    quit_browser()
    final = {v["id"]: v for v in states(profile).values()}
    assert e not in final
    assert any(v["id"] not in mapping.values() and v["close_clock"] == "0"
               for v in final.values())
    dump("recovery_starts_regular_residency", True)
    dump("passed", True)


def check_startup(mapping):
    mode = a.startup_check or "continue"
    choice = {"continue": 1, "new-tab": 5, "urls": 4}[mode]
    startup_url = f"http://127.0.0.1:{server.server_port}/startup-target"
    wd("POST", sid + "/url", {"url": "chrome://settings/onStartup"})
    for key, value in [
        ("session.startup_urls", [startup_url]),
        ("session.restore_on_startup", choice),
        *([("helium.tabs.cleanup_move_hours", 0)] if a.never_check else []),
    ]:
        result = asyncjs(
            "const done=arguments[arguments.length-1];chrome.settingsPrivate.setPref(arguments[0],arguments[1], '', ok=>done({ok,error:chrome.runtime.lastError?.message}));",
            key,
            value,
        )
        assert result.get("ok") and not result.get("error"), (key, result)
    selected = asyncjs(
        "chrome.settingsPrivate.getPref('session.restore_on_startup',arguments[arguments.length-1]);"
    )
    assert selected["value"] == choice, selected
    dump("startup_preference", selected)
    wd("POST", sid + "/url", {"url": f"chrome-extension://{ident}/fixture.html"})
    quit_browser()
    before = {v["id"]: v for v in states(profile).values()}
    older_ids = [mapping[role] for role in "BCEFG"]
    assert all(before[identity]["close_clock"] != "0" for identity in older_ids), before
    dump("before_quit_older", {identity: before[identity] for identity in older_ids})
    launch("startup", startup_mode=mode)
    time.sleep(5)
    reopened = tabs()
    dump("startup_tabs", reopened)
    sample_urls = {
        f"http://127.0.0.1:{server.server_port}/{role}" for role in "ABCDEFG"
    }
    actual_urls = {t["url"] for t in reopened}
    if mode == "continue":
        assert sample_urls <= actual_urls, actual_urls
    else:
        assert not sample_urls.intersection(actual_urls), actual_urls
        if mode == "urls":
            assert startup_url in actual_urls, actual_urls
        else:
            assert any(
                url.startswith("chrome://newtab") for url in actual_urls
            ), actual_urls
    if a.never_check:
        wd("POST", sid + "/url", {"url": "chrome://settings/appearance"})
        restored_pref = asyncjs(
            "chrome.settingsPrivate.getPref('helium.tabs.cleanup_move_hours',arguments[arguments.length-1]);"
        )
        assert restored_pref["value"] == 0, restored_pref
        dump("never_persisted_after_restart", restored_pref)
    quit_browser()
    after = {v["id"]: v for v in states(profile).values()}
    dump("startup_persisted_states", after)
    if mode == "continue":
        for identity in older_ids:
            assert after[identity]["close_clock"] == before[identity]["close_clock"], (
                identity,
                before,
                after,
            )
            assert after[identity]["frozen"] == before[identity]["frozen"], (
                identity,
                before,
                after,
            )
    else:
        assert not any(v["close_clock"] != "0" for v in after.values()), after
    dump("passed", True)


def check_settings():
    wd("POST", sid + "/url", {"url": "chrome://settings/appearance"})
    find = """
function find(selector, root=document) {
  const direct=root.querySelector(selector); if(direct) return direct;
  for(const e of root.querySelectorAll('*')) {
    if(e.shadowRoot) {const child=find(selector,e.shadowRoot);if(child)return child;}
  }
  return null;
}
"""

    def js(code):
        return execute(find + code)

    def wait(code):
        for _ in range(100):
            if js(code):
                return
            time.sleep(0.1)
        raise AssertionError(code)

    def choose(ident, value):
        js(
            f"const e=find('#{ident}');const select=e.shadowRoot.querySelector('select');select.value='{value}';select.dispatchEvent(new Event('change',{{bubbles:true}}));"
        )

    def pref(key):
        return asyncjs(
            "chrome.settingsPrivate.getPref(arguments[0],arguments[arguments.length-1]);",
            key,
        )["value"]

    wait("return find('#olderTabsMoveAfter')?.pref?.value === 24;")
    assert (
        js("return find('#olderTabsMoveGrouped').label;")
        == "Move inactive tabs from groups"
    )
    assert (
        js("return find('#olderTabsMoveGrouped').subLabel;")
        == "Allow moving inactive tabs from tab groups to Older Tabs"
    )
    options = js(
        "return ['olderTabsMoveAfter','olderTabsCloseAfter'].map(id=>find('#'+id).menuOptions);"
    )
    assert [x["name"] for x in options[0]] == [
        "Never",
        "6 hours",
        "1 day",
        "2 days",
    ], options
    assert [x["name"] for x in options[1]] == [
        "Immediately",
        "1 day",
        "2 days",
        "3 days",
        "7 days",
        "Never",
    ], options
    assert js("return find('#olderTabsEnabled') === null;")
    assert pref("helium.tabs.cleanup_move_grouped") is False
    assert js("return find('#olderTabsCloseAfter').label;") == "Close Older Tabs after"
    assert pref("helium.tabs.cleanup_close_hours") == 72
    choose("olderTabsMoveAfter", 0)
    wait(
        "return find('#olderTabsDetails').opened === false && find('#olderTabsDetails').getBoundingClientRect().height === 0;"
    )
    assert pref("helium.tabs.cleanup_move_hours") == 0
    wd("POST", sid + "/url", {"url": "chrome://settings/appearance"})
    wait(
        "return find('#olderTabsMoveAfter')?.pref?.value === 0 && find('#olderTabsDetails')?.opened === false && find('#olderTabsDetails').getBoundingClientRect().height === 0;"
    )
    choose("olderTabsMoveAfter", 6)
    wait(
        "return find('#olderTabsDetails').opened === true && find('#olderTabsDetails').getBoundingClientRect().height > 0;"
    )
    js("find('#olderTabsMoveGrouped').click();")
    wait("return find('#olderTabsMoveGrouped').checked === true;")
    assert pref("helium.tabs.cleanup_move_grouped") is True
    js("find('#olderTabsMoveGrouped').click();")
    wait("return find('#olderTabsMoveGrouped').checked === false;")
    assert pref("helium.tabs.cleanup_move_grouped") is False
    choose("olderTabsCloseAfter", -1)
    assert pref("helium.tabs.cleanup_close_hours") == -1
    choose("olderTabsCloseAfter", 0)
    assert pref("helium.tabs.cleanup_close_hours") == 0
    choose("olderTabsMoveAfter", 24)
    choose("olderTabsCloseAfter", 72)
    text = js(
        "return find('settings-appearance-behavior-page').shadowRoot.textContent;"
    )
    assert "Keep tab returns it to the regular stack" not in text
    dump(
        "settings",
        {
            "options": options,
            "group_default_off": True,
            "organize_switch_removed": True,
            "default_close_hours": 72,
            "group_label_description_exact": True,
            "group_toggle_round_trip": True,
            "never_collapses_on_change_and_reload": True,
            "immediately_distinct_from_never": True,
            "standalone_keep_sentence_removed": True,
        },
    )


try:
    for _ in range(100):
        try:
            if wd("GET", "/status")["ready"]:
                break
        except requests.RequestException:
            pass
        time.sleep(0.1)
    launch("create")
    if a.settings_check:
        check_settings()
        quit_browser()
        dump("passed", True)
        raise SystemExit(0)
    for t in tabs():
        if not t["url"].startswith("chrome-extension:"):
            asyncjs(
                "chrome.tabs.remove(arguments[0], arguments[arguments.length-1]);",
                t["id"],
            )
    dashboard_id = tabs()[0]["id"]
    asyncjs(
        "chrome.tabs.update(arguments[0],{pinned:true},arguments[arguments.length-1]);",
        dashboard_id,
    )
    ids = {}
    for index, name in enumerate("ABCDEFG", 1):
        tab = asyncjs(
            "chrome.tabs.create({url:arguments[0],index:arguments[1],active:false},arguments[arguments.length-1]);",
            f"http://127.0.0.1:{server.server_port}/{name}",
            index,
        )
        ids[name] = tab["id"]
    if a.pinned_check:
        for role in "BC":
            asyncjs(
                "chrome.tabs.update(arguments[0],{pinned:true},arguments[arguments.length-1]);",
                ids[role],
            )
    if a.group_check:
        for role, collapsed in [("B", False), ("C", True)]:
            group_id = asyncjs(
                "chrome.tabs.group({tabIds:[arguments[0]]},arguments[arguments.length-1]);",
                ids[role],
            )
            asyncjs(
                "chrome.tabGroups.update(arguments[0],{title:arguments[1],collapsed:arguments[2]},arguments[arguments.length-1]);",
                group_id,
                "Grouped " + role,
                collapsed,
            )
    asyncjs(
        "chrome.tabs.update(arguments[0],{active:true},arguments[arguments.length-1]);",
        (
            dashboard_id
            if (
                a.group_check
                or a.immediate_check
                or a.pinned_check
                or a.startup_check
                or a.never_check
                or a.arrangement_check
            )
            else ids["A"]
        ),
    )
    time.sleep(5)
    dump(
        "initial_tabs",
        [
            {"title": t["title"], "index": t["index"], "pinned": t["pinned"]}
            for t in tabs()
        ],
    )
    initial_role_order = [
        (
            "dashboard"
            if t["url"].startswith("chrome-extension:")
            else t["url"].rsplit("/", 1)[-1]
        )
        for t in sorted(tabs(), key=lambda t: t["index"])
    ]
    quit_browser()
    mapping = seed(
        profile,
        review=a.review or bool(a.startup_check) or a.never_check,
        group_check=a.group_check,
        immediate_check=a.immediate_check,
        pinned_check=a.pinned_check,
        role_order=initial_role_order if a.pinned_check else None,
    )
    dump("seeded_ids", mapping)
    debug = launch("aged")
    time.sleep(5)
    # Locate by URL after real restore. In the default case Older rows sort by
    # frozen last use (F,B,C,E,G); the group case keeps B/C in their groups.
    restored = tabs()
    dump(
        "restored_tabs",
        [{"title": t["title"], "url": t["url"], "index": t["index"]} for t in restored],
    )
    # Remove an extra startup extension URL if startup restored the existing one.
    controls = [t for t in restored if t["url"].startswith("chrome-extension:")]
    if len(controls) > 1:
        keep = next((t for t in controls if t["pinned"]), controls[0])
        remove = [t["id"] for t in controls if t["id"] != keep["id"]]
        asyncjs(
            "chrome.tabs.remove(arguments[0],arguments[arguments.length-1]);", remove
        )
        # Reattach to the surviving fixture target without visiting Older tabs.
        time.sleep(0.5)
        target = next(
            x["id"]
            for x in requests.get(
                f"http://127.0.0.1:{debug}/json/list", timeout=10
            ).json()
            if x.get("type") == "page"
            and x.get("url", "").startswith(f"chrome-extension://{ident}/")
        )
        dashboard = next(
            h for h in wd("GET", sid + "/window/handles") if h.endswith(target)
        )
        wd("POST", sid + "/window", {"handle": dashboard})
    (ev / "live.json").write_text(
        json.dumps(
            {
                "sid": sid,
                "driver_port": port,
                "debug_port": debug,
                "profile": str(profile),
                "dashboard": dashboard,
                "extension_id": ident,
                "fixture_ids": mapping,
                "server_port": server.server_port,
            }
        )
    )
    dump("ready", {"debug_port": debug, "driver_port": port})
    if a.entry_clock_check:
        check_entry_clock(mapping)
        raise SystemExit(0)
    if a.arrangement_check:
        check_arrangement(mapping)
        quit_browser()
        dump("persisted_states", states(profile))
        raise SystemExit(0)
    if a.startup_check or a.never_check:
        check_startup(mapping)
        raise SystemExit(0)
    if a.pinned_check:
        by_role = {
            t["url"].rsplit("/", 1)[-1]: t
            for t in tabs()
            if t["url"].startswith("http:")
        }
        for role in "BC":
            assert by_role[role]["pinned"] and not by_role[role]["active"], by_role[
                role
            ]
        assert not by_role["D"]["pinned"]
        dump("background_pinned_tabs", [by_role[role] for role in "BC"])
    elif a.group_check:
        group_tabs = tabs()
        groups = asyncjs("chrome.tabGroups.query({},arguments[arguments.length-1]);")
        dump("restored_groups", groups)
        by_role = {
            t["url"].rsplit("/", 1)[-1]: t
            for t in group_tabs
            if t["url"].startswith("http:")
        }
        group_by_id = {g["id"]: g for g in groups}
        for role, collapsed in [("B", False), ("C", True)]:
            if a.move_grouped:
                assert by_role[role]["groupId"] == -1
            else:
                assert group_by_id[by_role[role]["groupId"]]["collapsed"] == collapsed
        if a.move_grouped:
            assert not groups, groups
        assert by_role["D"]["groupId"] == -1
    elif a.immediate_check:
        # G has an unload handler; every other overdue tab must close directly.
        protected = next(t for t in tabs() if t["url"].endswith("/G"))
        protection = asyncjs(
            "const done=arguments[arguments.length-1];chrome.scripting.executeScript({target:{tabId:arguments[0]},func:()=>{window.onbeforeunload=()=>true;}},result=>done({error:chrome.runtime.lastError?.message||null,count:result?.length}));",
            protected["id"],
        )
        assert not protection["error"], protection
        dump("unload_protection_installed", protection)
        start = time.monotonic()
        samples = 0
        while time.monotonic() - start < 330:
            time.sleep(10)
            if browser.poll() is not None:
                raise RuntimeError("Browser exited during direct-close test")
            current = states(profile)
            assert all(
                v["close_clock"] == "0" and v["frozen"] == "0" for v in current.values()
            ), current
            samples += 1
        dump("regular_only_session_samples", samples)
        remaining = tabs()
        roles = {
            t["url"].rsplit("/", 1)[-1]
            for t in remaining
            if t["url"].startswith("http:")
        }
        assert roles == {"A", "D", "G"}, roles
        dump("after_direct_close", remaining)
        recent = asyncjs(
            "chrome.sessions.getRecentlyClosed({},arguments[arguments.length-1]);"
        )
        closed = {x.get("tab", {}).get("url", "").rsplit("/", 1)[-1] for x in recent}
        assert set("BCEF") <= closed and "G" not in closed, closed
        dump("recently_closed", recent)
        dump(
            "recovered",
            asyncjs(
                'const done=arguments[arguments.length-1];chrome.sessions.getRecentlyClosed({},items=>{const item=items.find(x=>x.tab&&x.tab.url.endsWith("/C"));chrome.sessions.restore(item.tab.sessionId,result=>done(result));});'
            ),
        )
        asyncjs(
            "chrome.scripting.executeScript({target:{tabId:arguments[0]},func:()=>{window.onbeforeunload=null;}},arguments[arguments.length-1]);",
            protected["id"],
        )
        time.sleep(1)
    elif not a.interactive:
        protected = next(t for t in tabs() if t["url"].endswith("/G"))
        protection = asyncjs(
            "const done=arguments[arguments.length-1];chrome.scripting.executeScript({target:{tabId:arguments[0]},func:()=>{window.onbeforeunload=()=>true;}},result=>done({error:chrome.runtime.lastError?.message||null,count:result?.length}));",
            protected["id"],
        )
        assert not protection["error"], protection
        dump("unload_protection_installed", protection)
        start = time.monotonic()
        while time.monotonic() - start < 330:
            time.sleep(10)
            if browser.poll() is not None:
                raise RuntimeError("Browser exited during retention test")
        remaining = tabs()
        recent = asyncjs(
            "chrome.sessions.getRecentlyClosed({},arguments[arguments.length-1]);"
        )
        urls = [
            t["url"].rsplit("/", 1)[-1]
            for t in remaining
            if t["url"].startswith("http:")
        ]
        assert "E" not in urls, urls
        assert all(role in urls for role in "ABCDFG"), urls
        assert any(
            x.get("tab", {}).get("url", "").endswith("/E") for x in recent
        ), recent
        assert not any(
            x.get("tab", {}).get("url", "").endswith("/G") for x in recent
        ), recent
        dump("after_retention", remaining)
        dump("recently_closed", recent)
        restored = asyncjs(
            'const done=arguments[arguments.length-1];chrome.sessions.getRecentlyClosed({},items=>{const item=items.find(x=>x.tab&&x.tab.url.endsWith("/E"));chrome.sessions.restore(item.tab.sessionId,result=>done(result));});'
        )
        dump("recovered", restored)
        asyncjs(
            "chrome.scripting.executeScript({target:{tabId:arguments[0]},func:()=>{window.onbeforeunload=null;}},arguments[arguments.length-1]);",
            protected["id"],
        )
        time.sleep(1)
    else:
        # Keep the fixture available for native interaction until explicitly released.
        while not (ev / "finish").exists():
            time.sleep(2)
            if browser.poll() is not None:
                break
    if browser.poll() is None:
        quit_browser()
    persisted = states(profile)
    dump("persisted_states", persisted)
    if a.pinned_check:
        byid = {v["id"]: v for v in persisted.values()}
        for role in "BC":
            assert byid[mapping[role]]["close_clock"] == "0"
            assert byid[mapping[role]]["frozen"] == "0"
        # B keeps its old baseline: this is pin exclusion, not activation.
        assert int(byid[mapping["B"]]["age"]) < int(byid[mapping["A"]]["age"])
        # C's deliberately stale Older residency is repaired, still pinned.
        assert int(byid[mapping["C"]]["age"]) > int(byid[mapping["B"]]["age"])
        # An equally inactive regular D actually ages, proving cleanup ran.
        assert byid[mapping["D"]]["close_clock"] != "0"
        dump("passed", True)
    elif a.group_check:
        byid = {v["id"]: v for v in persisted.values()}
        for role in "BC":
            state = byid[mapping[role]]
            if a.move_grouped:
                assert state["close_clock"] != "0", (role, state)
                assert state["frozen"] == state["last_use"], (role, state)
            else:
                assert state["close_clock"] == "0", (role, state)
                assert state["frozen"] == "0", (role, state)
            assert int(state["age"]) < int(byid[mapping["A"]]["age"])
        # Equally overdue ungrouped D actually transitions, proving cleanup ran.
        assert byid[mapping["D"]]["close_clock"] != "0"
        assert byid[mapping["D"]]["frozen"] == byid[mapping["D"]]["last_use"]
        dump("passed", True)
    elif a.immediate_check:
        byid = {v["id"]: v for v in persisted.values()}
        assert all(
            v["close_clock"] == "0" and v["frozen"] == "0" for v in byid.values()
        ), byid
        assert all(mapping[role] not in byid for role in "BCEF")
        assert mapping["G"] in byid
        assert any(v["id"] not in mapping.values() for v in byid.values())
        dump("passed", True)
    elif not a.interactive:
        byid = {v["id"]: v for v in persisted.values()}
        assert byid[mapping["F"]]["frozen"] == byid[mapping["F"]]["last_use"]
        assert byid[mapping["B"]]["frozen"] == byid[mapping["B"]]["last_use"]
        assert byid[mapping["C"]]["frozen"] == byid[mapping["C"]]["last_use"]
        assert mapping["E"] not in byid
        recovered = [
            v
            for v in byid.values()
            if v["id"] not in mapping.values() and v["close_clock"] == "0"
        ]
        assert recovered, recovered
        dump("passed", True)
finally:
    if browser and browser.poll() is None:
        browser.terminate()
        try:
            browser.wait(timeout=15)
        except subprocess.TimeoutExpired:
            browser.kill()
            browser.wait()
    driver.terminate()
    driver.wait(timeout=15)
    server.shutdown()
    log.close()
