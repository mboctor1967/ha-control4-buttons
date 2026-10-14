"""No settings: it reuses the Control4 integration's connection."""
from homeassistant import config_entries

from . import C4_DOMAIN, DOMAIN


class Control4ButtonsFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if not self.hass.config_entries.async_entries(C4_DOMAIN):
            return self.async_abort(reason="no_control4")
        if user_input is not None:
            return self.async_create_entry(title="Control4 Custom Buttons", data={})
        return self.async_show_form(step_id="user")
