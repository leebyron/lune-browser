"""Strict reader/writer for the Ninja v4 dependency log also used by Siso.

Format reference: https://github.com/ninja-build/ninja/blob/master/src/deps_log.cc
Keep node IDs, dependency lists and nanosecond timestamps intact when relocating
paths. Unlike Ninja's recovery reader, reject incomplete/corrupt logs outright.
"""
from array import array
from dataclasses import dataclass
import os
from pathlib import Path
import struct
import sys
import tempfile


HEADER = b'# ninjadeps\n' + struct.pack('<I', 4)
MAX_RECORD = (1 << 19) - 1


@dataclass
class DepsLog:
    paths: list
    records: dict


def read(path):
    paths, records, names = [], {}, set()
    with Path(path).open('rb') as stream:
        if stream.read(len(HEADER)) != HEADER:
            raise ValueError('Unsupported dependency-log signature/version; expected Ninja v4')
        while prefix := stream.read(4):
            if len(prefix) != 4:
                raise ValueError('Truncated dependency-log record header')
            word = struct.unpack('<I', prefix)[0]
            size = word & 0x7fffffff
            if not size or size > MAX_RECORD or size % 4:
                raise ValueError('Invalid dependency-log record size')
            payload = stream.read(size)
            if len(payload) != size:
                raise ValueError('Truncated dependency-log record')
            if word & 0x80000000:
                if size < 12:
                    raise ValueError('Undersized dependency record')
                output, timestamp = struct.unpack_from('<IQ', payload)
                dependencies = array('I')
                dependencies.frombytes(payload[12:])
                if sys.byteorder != 'little':
                    dependencies.byteswap()
                if output >= len(paths) or (dependencies and max(dependencies) >= len(paths)):
                    raise ValueError('Dependency record references an unknown node ID')
                # Keep only the last record, in last-record order.
                records.pop(output, None)
                records[output] = (timestamp, dependencies)
            else:
                if size < 8:
                    raise ValueError('Empty dependency-log path')
                checksum = struct.unpack_from('<I', payload, size - 4)[0]
                raw = payload[:-4].rstrip(b'\0')
                if not raw or b'\0' in raw or len(payload[:-4]) - len(raw) > 3:
                    raise ValueError('Invalid dependency-log path padding')
                name = os.fsdecode(raw)
                if checksum != (~len(paths) & 0xffffffff) or name in names:
                    raise ValueError('Invalid dependency-log node checksum or duplicate path')
                paths.append(name)
                names.add(name)
    return DepsLog(paths, records)


def write(path, log, relocate=lambda name: name):
    """Atomically write a compact log, merging equivalent input path IDs."""
    paths, lookup, ids = [], {}, []
    for original in log.paths:
        name = relocate(original)
        if not name or '\0' in name:
            raise ValueError('Invalid relocated dependency path')
        if name not in lookup:
            lookup[name] = len(paths)
            paths.append(name)
        ids.append(lookup[name])
    outputs = set()
    for output in log.records:
        if ids[output] in outputs:
            raise ValueError('Relocation would merge distinct output records')
        outputs.add(ids[output])
    destination = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='.deps-', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(HEADER)
            for index, name in enumerate(paths):
                raw = os.fsencode(name)
                raw += b'\0' * (-len(raw) % 4)
                size = len(raw) + 4
                if size > MAX_RECORD:
                    raise ValueError('Relocated path exceeds dependency-log record limit')
                stream.write(struct.pack('<I', size))
                stream.write(raw)
                stream.write(struct.pack('<I', ~index & 0xffffffff))
            for output, (timestamp, dependencies) in log.records.items():
                size = 12 + 4 * len(dependencies)
                if size > MAX_RECORD:
                    raise ValueError('Dependency record exceeds format limit')
                stream.write(struct.pack('<IIQ', size | 0x80000000, ids[output], timestamp))
                mapped = array('I', (ids[index] for index in dependencies))
                if sys.byteorder != 'little':
                    mapped.byteswap()
                stream.write(mapped.tobytes())
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {'paths_before': len(log.paths), 'paths_after': len(paths),
            'outputs': len(log.records), 'relocated_paths': sum(a != b for a, b in
                zip(log.paths, (paths[index] for index in ids)))}
