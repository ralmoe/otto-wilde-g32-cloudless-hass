"""Konstanten für die OWG Integration."""

from __future__ import annotations

DOMAIN = "otto_wilde_g32"
INTEGRATION_NAME = "Otto Wilde Cloudless"

CONF_LISTEN_IP = "listen_ip"
CONF_TIMEOUT_SECONDS = "timeout_seconds"

DEFAULT_LISTEN_IP = "192.168.0.10"
DEFAULT_PORT = 4501
DEFAULT_TIMEOUT_SECONDS = 10

PACKET_MIN_LENGTH = 22
UNAVAILABLE_RAW_VALUE = 1500

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
