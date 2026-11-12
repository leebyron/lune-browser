"""Fixture-only SNSS reader: rewrites cleanup metadata, never a personal profile."""

import json, struct, time
from pathlib import Path

KEY = "helium.older_tabs.v1"
EPOCH = 11644473600


def timestamp(hours):
    return str(int((time.time() + EPOCH - hours * 3600) * 1000000))


def commands(path):
    blob = path.read_bytes()
    assert blob[:4] == b"SNSS" and struct.unpack_from("<i", blob, 4)[0] == 3, (
        path,
        blob[:8],
    )
    rows = []
    offset = 8
    while offset < len(blob):
        n = struct.unpack_from("<H", blob, offset)[0]
        offset += 2
        assert n > 0 and offset + n <= len(blob), (path, offset, n)
        rows.append((blob[offset], blob[offset + 1 : offset + n]))
        offset += n
    return rows


def string(data, offset):
    size = struct.unpack_from("<i", data, offset)[0]
    offset += 4
    text = data[offset : offset + size].decode()
    offset += (size + 3) // 4 * 4
    return text, offset


def extra(data):
    # Pickle header holds payload size, then session id and length-prefixed strings.
    ident = struct.unpack_from("<i", data, 4)[0]
    key, offset = string(data, 8)
    value, offset = string(data, offset)
    return ident, key, value


def pack_extra(ident, key, value):
    def packstr(text):
        b = text.encode()
        return struct.pack("<i", len(b)) + b + b"\0" * ((-len(b)) % 4)

    payload = struct.pack("<i", ident) + packstr(key) + packstr(value)
    return struct.pack("<I", len(payload)) + payload


def states(profile):
    result = {}
    paths = sorted((Path(profile) / "Default/Sessions").glob("Session_*"))
    for path in paths[-1:]:
        for cmd, data in commands(path):
            if cmd == 33:
                ident, key, value = extra(data)
                if key == KEY:
                    result[ident] = json.loads(value)
            elif cmd == 16:
                result.pop(struct.unpack_from("<i", data, 0)[0], None)
    return result


def seed(
    profile,
    review=False,
    group_check=False,
    immediate_check=False,
    pinned_check=False,
    role_order=None,
):
    paths = sorted((Path(profile) / "Default/Sessions").glob("Session_*"))
    current = states(profile)
    unique = {v["id"]: v for v in current.values()}
    ordered = sorted(unique.values(), key=lambda x: x["order"])
    assert len(ordered) == 8, (len(ordered), ordered)
    # Dashboard, A, B, C, D, E, F, G. B/C must age; E/G are due Older tabs.
    roles = role_order or ["dashboard", "A", "B", "C", "D", "E", "F", "G"]
    assert set(roles) == {"dashboard", *"ABCDEFG"} and len(roles) == 8
    fixtures = {}
    for i, (role, state) in enumerate(zip(roles, ordered)):
        state = state.copy()
        state["order"] = (i + 1) * 1024
        age = {"B": 48, "C": 72, "E": 240, "F": 26, "G": 264}.get(role, 0)
        if (group_check or pinned_check) and role == "D":
            age = 48
        state.update(
            last_use=timestamp(age), age=timestamp(age), close_clock="0", frozen="0"
        )
        if role in ("E", "F", "G") and not immediate_check:
            state["frozen"] = state["last_use"]
            state["close_clock"] = timestamp(
                0 if review else (192 if role in ("E", "G") else 1)
            )
        if pinned_check and role == "C":
            state["frozen"] = state["last_use"]
            state["close_clock"] = timestamp(192)
        fixtures[state["id"]] = state
    for path in paths[-1:]:
        rows = []
        for cmd, data in commands(path):
            if cmd == 33:
                ident, key, value = extra(data)
                if key == KEY:
                    old = json.loads(value)
                    if old["id"] in fixtures:
                        data = pack_extra(
                            ident,
                            key,
                            json.dumps(fixtures[old["id"]], separators=(",", ":")),
                        )
            rows.append(struct.pack("<H", 1 + len(data)) + bytes([cmd]) + data)
        path.write_bytes(b"SNSS" + struct.pack("<i", 3) + b"".join(rows))
    return {role: state["id"] for role, state in zip(roles, ordered)}
