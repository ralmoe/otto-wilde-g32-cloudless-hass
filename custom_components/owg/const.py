"""Konstanten für die OWG Integration."""

from __future__ import annotations

DOMAIN = "owg"
INTEGRATION_NAME = "OWG"

CONF_LISTEN_IP = "listen_ip"
CONF_TIMEOUT_SECONDS = "timeout_seconds"

DEFAULT_LISTEN_IP = "192.168.2.169"
DEFAULT_PORT = 4501
DEFAULT_TIMEOUT_SECONDS = 60

PACKET_MIN_LENGTH = 22
UNAVAILABLE_RAW_VALUE = 1500

SENSOR_NAMES: tuple[str, ...] = (
    "Zone 1 Temperature",
    "Zone 2 Temperature",
    "Zone 3 Temperature",
    "Zone 4 Temperature",
    "External Probe 1 Temperature",
    "External Probe 2 Temperature",
    "External Probe 3 Temperature",
    "External Probe 4 Temperature",
)
