"""One HA button per Control4 custom button and per Control4 macro."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, _json, get_director, press_custom_button, run_macro


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback) -> None:
    try:
        director = get_director(hass)
        screens = _json(await director.send_get_request("/api/v1/agents/custom_buttons")) or []
        macros = _json(await director.send_get_request("/api/v1/agents/macros")) or []
    except HomeAssistantError as err:
        raise ConfigEntryNotReady(err) from err
    device = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name="Control4 Custom Buttons",
                        manufacturer="Control4", model="Custom buttons and macros")
    entities: list[ButtonEntity] = []
    seen: set[int] = set()
    for screen in screens:
        for b in screen.get("buttons", []):
            if b["id"] not in seen:
                seen.add(b["id"])
                entities.append(CustomButton(device, b["id"], f"{screen['name']} {b['name']}"))
    entities += [MacroButton(device, m["id"], f"Macro {m['name']}") for m in macros]
    add(entities)


class _Base(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, device: DeviceInfo, item_id: int, name: str, kind: str) -> None:
        self._id = item_id
        self._attr_name = name
        self._attr_device_info = device
        self._attr_unique_id = f"{kind}_{item_id}"
        self._attr_extra_state_attributes = {f"control4_{kind}_id": item_id}


class CustomButton(_Base):
    _attr_icon = "mdi:gesture-tap-button"

    def __init__(self, device: DeviceInfo, item_id: int, name: str) -> None:
        super().__init__(device, item_id, name, "custom_button")

    async def async_press(self) -> None:
        await press_custom_button(self.hass, self._id)


class MacroButton(_Base):
    _attr_icon = "mdi:script-text-play"

    def __init__(self, device: DeviceInfo, item_id: int, name: str) -> None:
        super().__init__(device, item_id, name, "macro")

    async def async_press(self) -> None:
        await run_macro(self.hass, self._id)
