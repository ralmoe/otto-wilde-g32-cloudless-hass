"""Sensor entities for OWG integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OWGRuntimeData
from .const import DOMAIN, SENSOR_NAMES


@dataclass(frozen=True, kw_only=True)
class OWGTemperatureSensorDescription(SensorEntityDescription):
    """Beschreibung eines OWG Temperatur-Sensors."""


SENSOR_DESCRIPTIONS: tuple[OWGTemperatureSensorDescription, ...] = tuple(
    OWGTemperatureSensorDescription(
        key=f"temp_{index + 1}",
        name=name,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    )
    for index, name in enumerate(SENSOR_NAMES)
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OWG temperature sensors from a config entry."""
    runtime: OWGRuntimeData = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            OWGTemperatureSensor(entry, runtime, index, description)
            for index, description in enumerate(SENSOR_DESCRIPTIONS)
        ]
    )


class OWGTemperatureSensor(SensorEntity):
    """Representation of one OWG temperature sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        entry: ConfigEntry,
        runtime: OWGRuntimeData,
        sensor_index: int,
        description: OWGTemperatureSensorDescription,
    ) -> None:
        self.entity_description = description
        self._runtime = runtime
        self._sensor_index = sensor_index

        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "manufacturer": "Otto Wilde",
            "model": "OWG Grill",
            "name": "OWG",
        }

    @property
    def available(self) -> bool:
        """Return True if sensor has valid data."""
        return self._runtime.sensor_available[self._sensor_index]

    @property
    def native_value(self) -> float | None:
        """Return the current temperature value."""
        return self._runtime.temperatures[self._sensor_index]

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        remove_listener = self._runtime.register_listener(self._handle_runtime_update)
        self.async_on_remove(remove_listener)

    @callback
    def _handle_runtime_update(self) -> None:
        """Write entity state to Home Assistant."""
        self.async_write_ha_state()
