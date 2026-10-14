"""Press Control4 custom buttons and run Control4 macros from Home Assistant.

Reuses the director connection of the Control4 integration (core or lawtancool/hass-control4),
so no extra login is needed. The director object is looked up on every press because the
Control4 integration replaces it when it renews its session.
"""
from __future__ import annotations

import asyncio
import json
import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
DOMAIN = "control4_buttons"
C4_DOMAIN = "control4"
PLATFORMS = [Platform.BUTTON]


def _json(value):
    return json.loads(value) if isinstance(value, (str, bytes)) else value


def get_director(hass: HomeAssistant):
    """Return the live Control4 director from the Control4 integration."""
    for entry in hass.config_entries.async_entries(C4_DOMAIN):
        data = hass.data.get(C4_DOMAIN, {}).get(entry.entry_id)
        if data and data.get("director"):
            return data["director"]
    raise HomeAssistantError("Control4 integration is not loaded")


async def agent_device_id(director, agent: str) -> int | None:
    """The item id that accepts commands for a Control4 agent (custom_buttons, macros)."""
    commands = _json(await director.send_get_request(f"/api/v1/agents/{agent}/commands")) or []
    return commands[0]["deviceId"] if commands else None


async def press_custom_button(hass: HomeAssistant, button_id: int) -> None:
    director = get_director(hass)
    device = await agent_device_id(director, "custom_buttons")
    await director.send_post_request(f"/api/v1/items/{device}/commands", "PRESS_BUTTON", {"ID": button_id})
    await asyncio.sleep(0.3)
    await director.send_post_request(f"/api/v1/items/{device}/commands", "RELEASE_BUTTON", {"ID": button_id})
    _LOGGER.info("Pressed Control4 custom button %s", button_id)


async def run_macro(hass: HomeAssistant, macro_id: int) -> None:
    director = get_director(hass)
    device = await agent_device_id(director, "macros")
    await director.send_post_request(f"/api/v1/items/{device}/commands", "EXECUTE_MACRO", {"id": macro_id})
    _LOGGER.info("Ran Control4 macro %s", macro_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    async def _press(call: ServiceCall) -> None:
        await press_custom_button(hass, call.data["button_id"])

    async def _macro(call: ServiceCall) -> None:
        await run_macro(hass, call.data["macro_id"])

    hass.services.async_register(DOMAIN, "press_custom_button", _press,
                                 schema=vol.Schema({vol.Required("button_id"): cv.positive_int}))
    hass.services.async_register(DOMAIN, "run_macro", _macro,
                                 schema=vol.Schema({vol.Required("macro_id"): cv.positive_int}))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    for service in ("press_custom_button", "run_macro"):
        hass.services.async_remove(DOMAIN, service)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
