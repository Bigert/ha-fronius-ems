"""Diagnostics support for HA Fronius EMS."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data

TO_REDACT = {
    "password",
    "Authorization",
    "authorization",
    "response",
    "cnonce",
    "nonce",
}


async def async_get_config_entry_diagnostics(
    hass,
    config_entry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    return async_redact_data(
        {
            "entry": dict(config_entry.data),
            "options": dict(config_entry.options),
        },
        TO_REDACT,
    )
