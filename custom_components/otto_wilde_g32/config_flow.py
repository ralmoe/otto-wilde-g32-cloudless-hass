"""Config flow for OWG integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_GAS_BOTTLE_WEIGHT_KG,
    CONF_LISTEN_IP,
    CONF_TIMEOUT_SECONDS,
    DEFAULT_GAS_BOTTLE_WEIGHT_KG,
    DEFAULT_LISTEN_IP,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT_SECONDS,
    DOMAIN,
    INTEGRATION_NAME,
)


def _build_schema(
    listen_ip_default: str,
    port_default: int,
    timeout_default: int,
    gas_bottle_weight_default: float,
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_LISTEN_IP, default=listen_ip_default): str,
            vol.Required(CONF_PORT, default=port_default): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=65535)
            ),
            vol.Required(CONF_TIMEOUT_SECONDS, default=timeout_default): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=3600)
            ),
            vol.Required(
                CONF_GAS_BOTTLE_WEIGHT_KG,
                default=gas_bottle_weight_default,
            ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=100.0)),
        }
    )


class OWGConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OWG."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title=INTEGRATION_NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(
                listen_ip_default=DEFAULT_LISTEN_IP,
                port_default=DEFAULT_PORT,
                timeout_default=DEFAULT_TIMEOUT_SECONDS,
                gas_bottle_weight_default=DEFAULT_GAS_BOTTLE_WEIGHT_KG,
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "OWGOptionsFlow":
        """Get options flow."""
        return OWGOptionsFlow(config_entry)


class OWGOptionsFlow(config_entries.OptionsFlow):
    """Handle OWG options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Manage the OWG options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        listen_ip = self._config_entry.options.get(
            CONF_LISTEN_IP,
            self._config_entry.data.get(CONF_LISTEN_IP, DEFAULT_LISTEN_IP),
        )
        port = self._config_entry.options.get(
            CONF_PORT,
            self._config_entry.data.get(CONF_PORT, DEFAULT_PORT),
        )
        timeout_seconds = self._config_entry.options.get(
            CONF_TIMEOUT_SECONDS,
            self._config_entry.data.get(CONF_TIMEOUT_SECONDS, DEFAULT_TIMEOUT_SECONDS),
        )
        gas_bottle_weight_kg = self._config_entry.options.get(
            CONF_GAS_BOTTLE_WEIGHT_KG,
            self._config_entry.data.get(
                CONF_GAS_BOTTLE_WEIGHT_KG,
                DEFAULT_GAS_BOTTLE_WEIGHT_KG,
            ),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(
                listen_ip_default=listen_ip,
                port_default=port,
                timeout_default=timeout_seconds,
                gas_bottle_weight_default=gas_bottle_weight_kg,
            ),
        )
