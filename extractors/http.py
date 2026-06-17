"""Tiny stdlib HTTP helpers (no `requests` dependency)."""
import gzip
import json
import urllib.error
import urllib.request

from .base import USER_AGENT


def _open(req, timeout=30):
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", errors="ignore")


def get(url, headers=None, timeout=30):
    h = {"User-Agent": USER_AGENT, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}
    if headers:
        h.update(headers)
    return _open(urllib.request.Request(url, headers=h), timeout)


def get_json(url, headers=None, timeout=30):
    h = {"Accept": "application/json"}
    if headers:
        h.update(headers)
    return json.loads(get(url, h, timeout))


def post_json(url, payload, headers=None, timeout=30):
    data = json.dumps(payload).encode()
    h = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    return json.loads(_open(req, timeout))
