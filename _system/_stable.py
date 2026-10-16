"""Write a committed JSON file only when its content changed (2026-10-16).

The SEC-derived files in each company folder (fundamentals.json,
statements.json, segments.json, profile.json) are committed to git: they
change only when a company files, they are slow to rebuild from scratch
(companyfacts is megabytes per name), and they are the evidence the
analysis quoted. A refresh that changes nothing but the run date must
therefore leave the file alone; otherwise every daily run rewrites ~100
files and git stores a new copy of each.

write_json_if_changed() serialises the new payload, compares it with the
file on disk while ignoring the named volatile keys (by default the run
date `as_of` and the fetch time `fetched_at`; dotted paths reach nested
keys, and a `*` segment matches every key of an object or every item of a
list — "dividends.yields_display.*.value"), and writes atomically only when
something else differs. A file's `as_of` therefore means "the day this
content was produced", which stays true for as long as the file is not
rewritten.

Volatile third-party data (Nasdaq prices, the Street block, live returns)
lives in gitignored files instead and is written every time.
"""
import json
import os
import tempfile
import time

DEFAULT_VOLATILE = ("as_of", "fetched_at")


def _strip_path(obj, parts):
    """obj without the one dotted path `parts` (a list of segments). A `*`
    segment matches every key of an object or every item of a list (a
    trailing `*` on a list removes every item). Containers along the path are
    copied, never mutated; a path that does not exist leaves obj as it is."""
    if not parts:
        return obj
    key, rest = parts[0], parts[1:]
    if isinstance(obj, dict):
        keys = list(obj) if key == "*" else ([key] if key in obj else [])
        if not keys:
            return obj
        out = dict(obj)
        for k in keys:
            if rest:
                out[k] = _strip_path(obj[k], rest)
            else:
                del out[k]
        return out
    if isinstance(obj, list) and key == "*":
        return [_strip_path(v, rest) for v in obj] if rest else []
    return obj


def _strip(obj, volatile):
    """A copy of obj without the volatile keys (dotted paths for nested
    objects, `*` for every key / item at that level)."""
    if not isinstance(obj, dict):
        return obj
    out = obj
    for path in volatile:
        out = _strip_path(out, path.split("."))
    return out if out is not obj else dict(obj)


def canonical(obj, volatile=DEFAULT_VOLATILE):
    """Order-independent text of obj without its volatile keys. NaN / Infinity
    serialise as their JSON5 spellings on both sides, so they compare equal."""
    return json.dumps(_strip(obj, volatile), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def same_content(path, obj, volatile=DEFAULT_VOLATILE):
    """True when path holds JSON equal to obj apart from the volatile keys."""
    try:
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
    except (OSError, ValueError):
        return False
    try:
        new = json.loads(json.dumps(obj))   # round-trip: tuples -> lists, int keys -> str, as the file would hold
    except (TypeError, ValueError):
        return False
    return canonical(old, volatile) == canonical(new, volatile)


def _replace(tmp, path, attempts=20, pause=0.1):
    """os.replace, retried on Windows: replacing a file another process holds
    open (a reader, an indexer, a virus scanner) raises PermissionError there
    for a moment. POSIX never does; the retry is a no-op on the VM."""
    for i in range(attempts):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if i == attempts - 1:
                raise
            time.sleep(pause)


def write_json_if_changed(path, obj, volatile=DEFAULT_VOLATILE, **dump_kwargs):
    """Write obj to path (atomically, with json.dump(**dump_kwargs)) unless the
    file already holds the same content apart from the volatile keys.
    Returns True when the file was written, False when it was left untouched."""
    if same_content(path, obj, volatile):
        return False
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + os.path.basename(path) + ".", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, **dump_kwargs)
        _replace(tmp, path)   # a reader never sees a half-written file
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
    return True
