"""Konstanten für die OWG Integration."""

from __future__ import annotations

DOMAIN = "otto_wilde_g32"
INTEGRATION_NAME = "Otto Wilde Cloudless"

CONF_LISTEN_IP = "listen_ip"
CONF_TIMEOUT_SECONDS = "timeout_seconds"
CONF_GAS_BOTTLE_WEIGHT_KG = "gas_bottle_weight_kg"

DEFAULT_LISTEN_IP = "192.168.0.10"
DEFAULT_PORT = 4501
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_GAS_BOTTLE_WEIGHT_KG = 11.0

PACKET_MIN_LENGTH = 25
UNAVAILABLE_RAW_VALUE = 1500

GAS_LEVEL_OFFSET = 22
LID_STATUS_OFFSET = 24

SENSOR_NAMES: tuple[str, ...] = (
    "Zone 1",
    "Zone 2",
    "Zone 3",
    "Zone 4",
    "Kerntemperaturfühler 1",
    "Kerntemperaturfühler 2",
    "Kerntemperaturfühler 3",
    "Kerntemperaturfühler 4",
)
