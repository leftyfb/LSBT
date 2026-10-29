"""Home Assistant configuration flow for LSBT."""
import logging

import voluptuous as vol
from aiohttp import ClientError
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import AM_URL, DOMAIN, PM_URL
from .smartsheet import parse_routes

_LOGGER = logging.getLogger(__name__)


class BusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Choose schedule, then route, then a school from published data."""

    VERSION = 1

    def __init__(self):
        self._period = None
        self._route_data = None
        self._schools = []

    async def async_step_user(self, user_input=None):
        """Choose schedule first so the URL defaults to the correct sheet."""
        if user_input is not None:
            self._period = user_input["period"]
            return await self.async_step_route()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("period", default="PM"): vol.In(["PM", "AM"])}),
        )

    async def async_step_route(self, user_input=None):
        """Load the schools actually served by the chosen route."""
        if self._period is None:
            return await self.async_step_user()

        errors = {}
        if user_input is not None:
            route = user_input["route"].strip()
            if not route:
                errors["base"] = "invalid_selection"
            else:
                try:
                    session = async_get_clientsession(self.hass)
                    async with session.get(user_input["url"], timeout=20) as response:
                        response.raise_for_status()
                        content = await response.text()
                        content_type = response.headers.get("Content-Type", "")
                    routes = parse_routes(content, content_type)
                    matching = [
                        item for item in routes
                        if item["route"].casefold() == route.casefold()
                    ]
                    if not matching:
                        errors["base"] = "route_not_found"
                    else:
                        self._schools = sorted(
                            {
                                school["school"].strip()
                                for item in matching for school in item["schools"]
                                if school["school"].strip()
                            },
                            key=str.casefold,
                        )
                        if self._schools:
                            self._route_data = {**user_input, "route": route, "period": self._period}
                            return await self.async_step_school()
                        errors["base"] = "no_schools"
                except (ClientError, TimeoutError, ValueError) as exc:
                    _LOGGER.warning("Unable to discover schools: %s", exc)
                    errors["base"] = "cannot_connect"

        default_url = AM_URL if self._period == "AM" else PM_URL
        return self.async_show_form(
            step_id="route",
            data_schema=vol.Schema({
                vol.Required("route", default=(user_input or {}).get("route", "")): str,
                vol.Required("url", default=(user_input or {}).get("url", default_url)): str,
                vol.Required("interval", default=(user_input or {}).get("interval", 60)):
                    vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }),
            errors=errors,
        )

    async def async_step_school(self, user_input=None):
        """Select a school present on the route."""
        if self._route_data is None or not self._schools:
            return await self.async_step_user()

        if user_input is not None:
            school = user_input["school"]
            if school not in self._schools:
                return self.async_show_form(
                    step_id="school",
                    data_schema=self._school_schema(),
                    errors={"base": "invalid_selection"},
                )
            data = {**self._route_data, "school": school}
            route, period = data["route"], data["period"]
            await self.async_set_unique_id(
                f"{period.lower()}:{route.casefold()}:{school.casefold()}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=f"{period} {route} — {school}", data=data)

        return self.async_show_form(step_id="school", data_schema=self._school_schema())

    def _school_schema(self):
        return vol.Schema({
            vol.Required("school"): SelectSelector(
                SelectSelectorConfig(options=self._schools, mode=SelectSelectorMode.DROPDOWN)
            ),
        })
