"""Configuration UI."""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, PM_URL

class BusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
            route = user_input["route"].strip()
            school = user_input["school"].strip()
            if not route or not school:
                return self.async_show_form(step_id="user", data_schema=self.schema(), errors={"base": "invalid_selection"})
            await self.async_set_unique_id(f'{user_input["period"].lower()}:{route.casefold()}:{school.casefold()}')
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f'{user_input["period"]} {route} — {school}', data=user_input)
        return self.async_show_form(step_id="user", data_schema=self.schema())

    @staticmethod
    def schema():
        return vol.Schema({
            vol.Required("period", default="PM"): vol.In(["PM", "AM"]),
            vol.Required("route"): str,
            vol.Required("school"): str,
            vol.Required("url", default=PM_URL): str,
            vol.Required("interval", default=60): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
        })
