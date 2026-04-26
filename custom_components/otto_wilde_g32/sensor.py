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
from homeassistant.const import PERCENTAGE, UnitOfMass, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OWGRuntimeData
from .const import DOMAIN, SENSOR_NAMES, UNAVAILABLE_RAW_VALUE


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
    """Set up OWG sensors from a config entry."""
    runtime: OWGRuntimeData = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        OWGTemperatureSensor(entry, runtime, index, description)
        for index, description in enumerate(SENSOR_DESCRIPTIONS)
    ]
    entities.extend(
        [
            OWGGasLevelPercentSensor(entry, runtime),
            OWGGasLevelKgSensor(entry, runtime),
        ]
    )

    async_add_entities(entities)


class OWGBaseSensor(SensorEntity):
    """Common base class for OWG sensor entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _watched_runtime_fields: frozenset[str] = frozenset()

    def __init__(self, entry: ConfigEntry, runtime: OWGRuntimeData) -> None:
        self._runtime = runtime
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "manufacturer": "Otto Wilde",
            "model": "G32",
            "name": "Otto Wilde G32",
        }

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        remove_listener = self._runtime.register_listener(self._handle_runtime_update)
        self.async_on_remove(remove_listener)

    @callback
    def _handle_runtime_update(self, changed_fields: set[str]) -> None:
        """Write entity state to Home Assistant when relevant runtime fields changed."""
        if changed_fields & self._watched_runtime_fields:
            self.async_write_ha_state()


class OWGTemperatureSensor(OWGBaseSensor):
    """Representation of one OWG temperature sensor."""

    def __init__(
        self,
        entry: ConfigEntry,
        runtime: OWGRuntimeData,
        sensor_index: int,
        description: OWGTemperatureSensorDescription,
    ) -> None:
        super().__init__(entry, runtime)
        self.entity_description = description
        self._sensor_index = sensor_index
        self._watched_runtime_fields = frozenset({f"temperature_{sensor_index}"})
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    def _current_temperature(self) -> float | None:
        """Return the current runtime temperature with unavailable guard."""
        value = self._runtime.temperatures[self._sensor_index]

        # Defensive guard: disconnected probes may still surface as literal 1500.0
        # from upstream payload handling. Home Assistant should treat this as
        # unavailable, not as a real temperature value.
        if value == float(UNAVAILABLE_RAW_VALUE):
            return None

        return value

    @property
    def available(self) -> bool:
        """Return True if sensor has valid data."""
        return (
            self._runtime.sensor_available[self._sensor_index]
            and self._current_temperature() is not None
        )

    @property
    def native_value(self) -> float | None:
        """Return the current temperature value."""
        return self._current_temperature()


class OWGGasLevelPercentSensor(OWGBaseSensor):
    """Sensor for gas bottle fill level in percent."""

    _attr_name = "Füllstand Gasflasche"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1
    _watched_runtime_fields = frozenset({"gas"})

    def __init__(self, entry: ConfigEntry, runtime: OWGRuntimeData) -> None:
        super().__init__(entry, runtime)
        self._attr_unique_id = f"{entry.entry_id}_gas_fill_percent"

    @property
    def available(self) -> bool:
        return self._runtime.gas_level_percent is not None

    @property
    def native_value(self) -> float | None:
        return self._runtime.gas_level_percent


class OWGGasLevelKgSensor(OWGBaseSensor):
    """Sensor for gas bottle fill amount in kg."""

    _attr_name = "Füllmenge Gasflasche"
    _attr_device_class = SensorDeviceClass.WEIGHT
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 3
    _watched_runtime_fields = frozenset({"gas"})

    def __init__(self, entry: ConfigEntry, runtime: OWGRuntimeData) -> None:
        super().__init__(entry, runtime)
        self._attr_unique_id = f"{entry.entry_id}_gas_fill_kg"

    @property
    def available(self) -> bool:
        return self._runtime.gas_level_kg is not None

    @property
    def native_value(self) -> float | None:
        return self._runtime.gas_level_kg
