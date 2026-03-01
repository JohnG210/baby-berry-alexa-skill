"""
Thin authentication wrapper for the huckleberry-api package.

Re-authenticates on every call — Lambda is stateless and invocations may hit
fresh containers at any time.

Note: the exact class name / login method below reflects common patterns for
the huckleberry-api PyPI package. Adjust if the package exposes a different
interface (e.g. `from huckleberry import HuckleberryClient`).
"""
import os

from huckleberry_api import HuckleberryAPI  # adjust if import path differs


def get_client():
    """Return an authenticated (api, child_uid) tuple from env vars."""
    email = os.environ["HUCKLEBERRY_EMAIL"]
    password = os.environ["HUCKLEBERRY_PASSWORD"]
    child_uid = os.environ["HUCKLEBERRY_CHILD_UID"]

    api = HuckleberryAPI()
    api.login(email=email, password=password)

    return api, child_uid
