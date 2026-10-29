"""Fetch remote data via Home Assistant's shared aiohttp session."""
from datetime import timedelta
import logging
from aiohttp import ClientError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .smartsheet import parse_routes, find_school

class BusCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, logging.getLogger(__name__), name=entry.title,
                         update_interval=timedelta(seconds=entry.data["interval"]))
        self.entry = entry

    async def _async_update_data(self):
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(self.entry.data["url"], timeout=20) as response:
                response.raise_for_status()
                body = await response.text()
                content_type = response.headers.get("Content-Type", "")
            result = find_school(parse_routes(body, content_type),
                                 self.entry.data["route"], self.entry.data["school"])
            if result is None:
                raise ValueError("Selected route and school not found")
            return result
        except (ClientError, TimeoutError, ValueError) as exc:
            raise UpdateFailed(f"Unable to read public bus data: {exc}") from exc
