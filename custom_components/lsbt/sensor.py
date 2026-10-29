"""Delay, covering bus and route status sensors."""
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

FIELDS = (
    SensorEntityDescription(key="minutes_late", name="Minutes late", native_unit_of_measurement="min", icon="mdi:clock-alert-outline"),
    SensorEntityDescription(key="covering_bus", name="Covering bus", icon="mdi:bus"),
    SensorEntityDescription(key="status", name="Status", icon="mdi:bus-clock"),
)

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(BusSensor(entry, desc) for desc in FIELDS)

class BusSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, entry, description):
        super().__init__(entry.runtime_data)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f'{entry.data["period"]} Bus {entry.data["route"]} — {entry.data["school"]}',
            "manufacturer": "Lowell Public Schools (unofficial)",
        }

    @property
    def native_value(self):
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self):
        return {"route": self.coordinator.data["route"], "school": self.coordinator.data["school"], "source": self.coordinator.entry.data["url"]}
