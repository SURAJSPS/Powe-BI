"""Signed browser cookie for Streamlit login persistence (survives refresh / new server session)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import unquote

import streamlit as st
import streamlit.components.v1 as components

SESSION_COOKIE_NAME = "rnk_civil_auth"
# 14 days
_MAX_AGE_SEC = 14 * 24 * 60 * 60


def _secret_bytes(secret: str) -> bytes:
    return hashlib.sha256(secret.encode("utf-8")).digest()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def sign_session(user_id: str, *, secret: str) -> str:
    """Return a compact signed token (ASCII safe for cookies)."""
    now = int(time.time())
    payload = {"uid": user_id, "iat": now, "exp": now + _MAX_AGE_SEC}
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = hmac.new(_secret_bytes(secret), raw, hashlib.sha256).digest()
    return _b64url(raw) + "." + _b64url(sig)


def verify_session(token: str, *, secret: str) -> str | None:
    """Return user_id if signature and expiry are valid."""
    if not token or "." not in token:
        return None
    try:
        raw_b64, sig_b64 = token.split(".", 1)
        raw = _b64url_decode(raw_b64)
        sig = _b64url_decode(sig_b64)
        expect = hmac.new(_secret_bytes(secret), raw, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expect):
            return None
        data: dict[str, Any] = json.loads(raw.decode("utf-8"))
        uid = data.get("uid")
        exp = int(data.get("exp", 0))
        if not isinstance(uid, str) or not uid or exp < int(time.time()):
            return None
        return uid
    except Exception:
        return None


def _parse_cookie_header_value(header_val: str, name: str) -> str | None:
    """Extract one cookie value from a raw Cookie header string."""
    if not header_val:
        return None
    for part in header_val.split(";"):
        part = part.strip()
        if not part.startswith(name + "="):
            continue
        raw = part[len(name) + 1 :].strip()
        if not raw:
            return None
        try:
            return unquote(raw)
        except Exception:
            return raw
    return None


def _cookie_header_string() -> str | None:
    """Best-effort Cookie header from st.context (varies by Streamlit version)."""
    try:
        h = st.context.headers
        v = h.get("Cookie") or h.get("cookie")
        if v:
            return v
        if hasattr(h, "get_all"):
            for key in ("Cookie", "cookie"):
                parts = h.get_all(key)
                if parts:
                    return parts[-1]
    except Exception:
        pass
    return None


def get_cookie_token() -> str | None:
    """Read session token from the browser (Streamlit context cookies or Cookie header fallback)."""
    try:
        cookies = st.context.cookies
        if cookies:
            for key in (SESSION_COOKIE_NAME, SESSION_COOKIE_NAME.lower()):
                v = cookies.get(key)
                if v:
                    return str(v)
    except Exception:
        pass
    raw_header = _cookie_header_string()
    return _parse_cookie_header_value(raw_header or "", SESSION_COOKIE_NAME)


def inject_set_cookie(token: str) -> None:
    """Tell the browser to store the session cookie (component iframe + parent when same-origin)."""
    tok_js = json.dumps(token)
    name_js = json.dumps(SESSION_COOKIE_NAME)
    components.html(
        f"""
<script>
(function() {{
  var t = {tok_js};
  var n = {name_js};
  var secure = (typeof location !== "undefined" && location.protocol === "https:") ? "; Secure" : "";
  var c = n + "=" + encodeURIComponent(t) + "; path=/; max-age={_MAX_AGE_SEC}; SameSite=Lax" + secure;
  try {{
    document.cookie = c;
    if (window.parent && window.parent !== window) {{
      try {{ window.parent.document.cookie = c; }} catch (e) {{}}
    }}
  }} catch (e) {{}}
}})();
</script>
""",
        height=0,
        width=0,
    )


def inject_clear_cookie() -> None:
    """Remove the session cookie in the browser."""
    name_js = json.dumps(SESSION_COOKIE_NAME)
    components.html(
        f"""
<script>
(function() {{
  var n = {name_js};
  document.cookie = n + "=; path=/; max-age=0; SameSite=Lax";
  try {{
    if (window.parent && window.parent !== window) {{
      window.parent.document.cookie = n + "=; path=/; max-age=0; SameSite=Lax";
    }}
  }} catch (e) {{}}
}})();
</script>
""",
        height=0,
        width=0,
    )
