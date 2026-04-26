"""OWG Home Assistant Integration."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import contextlib
import logging
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_GAS_BOTTLE_WEIGHT_KG,
    CONF_LISTEN_IP,
    CONF_TIMEOUT_SECONDS,
    DEFAULT_GAS_BOTTLE_WEIGHT_KG,
    DEFAULT_LISTEN_IP,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT_SECONDS,
    DOMAIN,
    GAS_LEVEL_OFFSET,
    LID_STATUS_OFFSET,
    PACKET_MIN_LENGTH,
    UNAVAILABLE_RAW_VALUE,
)

_LOGGER = logging.getLogger(__name__)


class OWGRuntimeData:
    """Laufzeitdaten und TCP-Listener für OWG."""

    def __init__(self, grill_ip: str, port: int, timeout_seconds: int, gas_bottle_weight_kg: float) -> None:
        self.grill_ip = grill_ip
        self.port = port
        self.timeout_seconds = timeout_seconds
        self.gas_bottle_weight_kg = gas_bottle_weight_kg

        self.temperatures: list[float | None] = [None] * 8
        self.sensor_available: list[bool] = [False] * 8
        self.lid_open: bool | None = None
        self.gas_level_percent: float | None = None
        self.gas_level_kg: float | None = None
        self.last_packet_ts: float | None = None

        self._listeners: set[Callable[[set[str]], None]] = set()
        self._server: asyncio.AbstractServer | None = None
        self._timeout_task: asyncio.Task[None] | None = None

    def register_listener(self, listener: Callable[[set[str]], None]) -> Callable[[], None]:
        """Registriert einen Listener für Statusupdates."""
        self._listeners.add(listener)

        def _remove() -> None:
            self._listeners.discard(listener)

        return _remove

    def _notify_listeners(self, changed_fields: set[str]) -> None:
        for listener in tuple(self._listeners):
            listener(changed_fields)

    async def async_start(self) -> None:
        """Startet TCP-Server und Timeout-Überwachung."""
        self._server = await asyncio.start_server(
            self._handle_client,
            host="0.0.0.0",
            port=self.port,
        )
        _LOGGER.info("OWG TCP-Listener gestartet auf 0.0.0.0:%s", self.port)

        self._timeout_task = asyncio.create_task(
            self._timeout_watchdog(),
            name="owg-timeout-watchdog",
        )

    async def async_stop(self) -> None:
        """Stoppt TCP-Server und Background-Tasks sauber."""
        if self._timeout_task:
            self._timeout_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._timeout_task
            self._timeout_task = None

        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
            _LOGGER.info("OWG TCP-Listener gestoppt")

    async def _timeout_watchdog(self) -> None:
        """Setzt Sensoren auf unavailable, wenn keine Daten mehr eintreffen."""
        while True:
            await asyncio.sleep(1)

            if self.last_packet_ts is None:
                continue

            if time.monotonic() - self.last_packet_ts <= self.timeout_seconds:
                continue

            if (
                any(self.sensor_available)
                or self.lid_open is not None
                or self.gas_level_percent is not None
                or self.gas_level_kg is not None
            ):
                _LOGGER.warning(
                    "OWG Timeout nach %s Sekunden ohne Daten. Sensoren werden unavailable gesetzt.",
                    self.timeout_seconds,
                )
                self.sensor_available = [False] * 8
                self.temperatures = [None] * 8
                self.lid_open = None
                self.gas_level_percent = None
                self.gas_level_kg = None
                self._notify_listeners(
                    {"lid", "gas", *(f"temperature_{index}" for index in range(8))}
                )

    async def _handle_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Verarbeitet eine eingehende TCP-Verbindung."""
        peername = writer.get_extra_info("peername")
        peer_ip = peername[0] if isinstance(peername, tuple) else None

        if peer_ip and self.grill_ip and peer_ip != self.grill_ip:
            _LOGGER.warning(
                "Verbindung von unerwarteter Quelle %s abgewiesen (erwartet: %s)",
                peer_ip,
                self.grill_ip,
            )
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()
            return

        _LOGGER.debug("OWG Verbindung angenommen von %s", peer_ip or "unbekannt")

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                self._process_payload(data)
        except Exception:  # pragma: no cover - defensive logging
            _LOGGER.exception("Fehler beim Verarbeiten der OWG TCP-Verbindung")
        finally:
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()

    def _decode_gas(self, payload: bytes) -> tuple[float | None, float | None]:
        """Dekodiert Gasgewicht in kg und Prozent aus Bytes 22+23 (Big Endian, Gramm)."""
        gas_raw_grams = int.from_bytes(payload[GAS_LEVEL_OFFSET : GAS_LEVEL_OFFSET + 2], byteorder="big")

        if gas_raw_grams == 0:
            return None, None

        gas_kg = round(gas_raw_grams / 1000.0, 3)
        max_fill_kg = max(self.gas_bottle_weight_kg, 0.1)
        gas_percent = round(min((gas_kg / max_fill_kg) * 100.0, 100.0), 1)

        return gas_kg, gas_percent

    def _process_payload(self, payload: bytes) -> None:
        """Dekodiert Sensorwerte aus einem OWG-Paket."""
        if len(payload) < PACKET_MIN_LENGTH:
            _LOGGER.debug("Ignoriere zu kurzes OWG-Paket mit %s Bytes", len(payload))
            return

        temperatures: list[float | None] = []
        availability: list[bool] = []

        for index in range(8):
            byte_1 = payload[6 + index * 2]
            byte_2 = payload[7 + index * 2]
            raw_value = byte_1 * 100 + byte_2

            if raw_value == UNAVAILABLE_RAW_VALUE:
                temperatures.append(None)
                availability.append(False)
                continue

            temperatures.append(raw_value / 10)
            availability.append(True)

        lid_raw = payload[LID_STATUS_OFFSET]
        lid_open = lid_raw == 0x01
        gas_kg, gas_percent = self._decode_gas(payload)

        changed_fields: set[str] = set()
        for index, (old_temp, old_available, new_temp, new_available) in enumerate(
            zip(self.temperatures, self.sensor_available, temperatures, availability, strict=False)
        ):
            if old_temp != new_temp or old_available != new_available:
                changed_fields.add(f"temperature_{index}")

        if self.lid_open != lid_open:
            changed_fields.add("lid")

        if self.gas_level_percent != gas_percent or self.gas_level_kg != gas_kg:
            changed_fields.add("gas")

        self.temperatures = temperatures
        self.sensor_available = availability
        self.lid_open = lid_open
        self.gas_level_percent = gas_percent
        self.gas_level_kg = gas_kg
        self.last_packet_ts = time.monotonic()

        if changed_fields:
            self._notify_listeners(changed_fields)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OWG from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    grill_ip = entry.options.get(CONF_LISTEN_IP, entry.data.get(CONF_LISTEN_IP, DEFAULT_LISTEN_IP))
    port = entry.options.get(CONF_PORT, entry.data.get(CONF_PORT, DEFAULT_PORT))
    timeout_seconds = entry.options.get(
        CONF_TIMEOUT_SECONDS,
        entry.data.get(CONF_TIMEOUT_SECONDS, DEFAULT_TIMEOUT_SECONDS),
    )
    gas_bottle_weight_kg = float(
        entry.options.get(
            CONF_GAS_BOTTLE_WEIGHT_KG,
            entry.data.get(CONF_GAS_BOTTLE_WEIGHT_KG, DEFAULT_GAS_BOTTLE_WEIGHT_KG),
        )
    )

    runtime = OWGRuntimeData(
        grill_ip=grill_ip,
        port=port,
        timeout_seconds=timeout_seconds,
        gas_bottle_weight_kg=gas_bottle_weight_kg,
    )

    try:
        await runtime.async_start()
    except OSError as err:
        raise ConfigEntryNotReady(
            f"OWG TCP-Listener konnte nicht gestartet werden auf 0.0.0.0:{port}: {err}"
        ) from err

    hass.data[DOMAIN][entry.entry_id] = runtime
    await hass.config_entries.async_forward_entry_setups(
        entry,
        [Platform.SENSOR, Platform.BINARY_SENSOR],
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload OWG config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        [Platform.SENSOR, Platform.BINARY_SENSOR],
    )

    runtime: OWGRuntimeData | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if runtime is not None:
        await runtime.async_stop()

    if not hass.data.get(DOMAIN):
        hass.data.pop(DOMAIN, None)

    return unload_ok
