"""Binary sensor entities for OWG integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OWGRuntimeData
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OWG binary sensors from a config entry."""
    runtime: OWGRuntimeData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OWGLidBinarySensor(entry, runtime)])


class OWGLidBinarySensor(BinarySensorEntity):
    """Deckelstatus des Grills."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_name = "Deckelstatus"
    _attr_device_class = BinarySensorDeviceClass.OPENING

    def __init__(self, entry: ConfigEntry, runtime: OWGRuntimeData) -> None:
        self._runtime = runtime
        self._attr_unique_id = f"{entry.entry_id}_lid_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "manufacturer": "Otto Wilde",
            "model": "G32",
            "name": "Otto Wilde G32",
        }

    @property
    def available(self) -> bool:
        """Return if lid state is known from runtime packets."""
        return self._runtime.lid_open is not None

    @property
    def is_on(self) -> bool | None:
        """Return True when the lid is open."""
        return self._runtime.lid_open

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        remove_listener = self._runtime.register_listener(self._handle_runtime_update)
        self.async_on_remove(remove_listener)

    @callback
    def _handle_runtime_update(self) -> None:
        """Write entity state to Home Assistant."""
        self.async_write_ha_state()
