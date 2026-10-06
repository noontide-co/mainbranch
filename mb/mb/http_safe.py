"""An HTTP opener that never follows a redirect.

urllib's default redirect handler copies a request's headers, including
``Authorization``, onto the redirected request, so a 3xx from a provider would
send the credential to a ``Location`` URL that ``mb`` did not choose. Every
request that carries a credential goes through :func:`open_no_redirect`
instead. A 3xx raises ``urllib.error.HTTPError`` with the 3xx code, exactly
like any other non-2xx answer, and no second request is made.

Requests without a credential (the public PyPI version check, the fal.ai image
download) may keep following redirects through plain ``urlopen``.
"""

from __future__ import annotations

import urllib.request
from typing import Any


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect; the 3xx comes back as an ``HTTPError``."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def open_no_redirect(request: urllib.request.Request, timeout: float) -> Any:
    """Open ``request`` without following any redirect."""
    return OPENER.open(request, timeout=timeout)


def is_redirect(status: int) -> bool:
    return 300 <= status < 400
