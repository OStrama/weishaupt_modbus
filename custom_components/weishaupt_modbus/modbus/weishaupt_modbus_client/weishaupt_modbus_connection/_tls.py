"""Build TLS contexts for Modbus connections."""

from __future__ import annotations

import os
import ssl


def build_tls_context(
    verify: bool | str,
    check_hostname: bool,
    client_cert: str | None,
    client_key: str | None,
    client_key_password: str | None,
) -> ssl.SSLContext:
    """Build a client TLS context."""
    if isinstance(verify, str):
        if os.path.isdir(verify):
            context = ssl.create_default_context(capath=verify)
        else:
            context = ssl.create_default_context(cafile=verify)
    else:
        context = ssl.create_default_context()
        if not verify:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
    if verify and not check_hostname:
        context.check_hostname = False  # still verifies the cert, skips the name
    if client_cert is not None:
        context.load_cert_chain(client_cert, client_key, client_key_password)
    return context
