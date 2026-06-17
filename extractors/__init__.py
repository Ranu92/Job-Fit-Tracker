"""Router: pick the right adapter for a URL, with a generic Playwright fallback.

Order matters — known job-board APIs (reliable + dated) are tried before the
generic renderer. LinkedIn falls back to generic if the guest API is blocked.
"""
from . import ashby, generic, greenhouse, lever, linkedin, workday

_API_ADAPTERS = [workday, greenhouse, lever, ashby, linkedin]


def fetch(url: str):
    """Return (jobs, adapter_name). Raises only if even the fallback fails."""
    for mod in _API_ADAPTERS:
        if mod.matches(url):
            name = mod.__name__.split(".")[-1]
            try:
                jobs = mod.fetch(url)
            except Exception as e:
                jobs = []
                print(f"  [{name}] error: {e}")
            if jobs:
                return jobs, name
            # LinkedIn / others: empty result -> try generic render as fallback
            try:
                gjobs = generic.fetch(url)
                if gjobs:
                    return gjobs, f"{name}->generic"
            except Exception as e:
                print(f"  [generic fallback] {e}")
            return jobs, name
    # No known adapter -> generic
    return generic.fetch(url), "generic"
