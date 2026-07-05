"""Sensor platform for MeshWald."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPressure, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MeshWaldCoordinator


@dataclass(frozen=True, kw_only=True)
class MeshWaldSensorDescription(SensorEntityDescription):
    """Describes how to read one metric out of a /data/sensors/{node} reading."""

    value_key: str = ""


SENSOR_TYPES: tuple[MeshWaldSensorDescription, ...] = (
    MeshWaldSensorDescription(
        key="temperature",
        value_key="temperature_c",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeshWaldSensorDescription(
        key="humidity",
        value_key="humidity_pct",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeshWaldSensorDescription(
        key="pressure",
        value_key="pressure_hpa",
        translation_key="pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    MeshWaldSensorDescription(
        key="iaq",
        value_key="iaq",
        translation_key="iaq",
        device_class=SensorDeviceClass.AQI,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up MeshWald sensors from a config entry."""
    coordinator: MeshWaldCoordinator = hass.data[DOMAIN][entry.entry_id]
    known_nodes: set[str] = set()

    @callback
    def _add_new_nodes() -> None:
        new_nodes = set(coordinator.data) - known_nodes
        if not new_nodes:
            return
        known_nodes.update(new_nodes)
        async_add_entities(
            MeshWaldSensor(coordinator, entry, node, description)
            for node in new_nodes
            for description in SENSOR_TYPES
        )

    _add_new_nodes()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_nodes))


class MeshWaldSensor(CoordinatorEntity[MeshWaldCoordinator], SensorEntity):
    """A single metric (temperature, humidity, ...) of one MeshWald node."""

    _attr_has_entity_name = True
    entity_description: MeshWaldSensorDescription

    def __init__(
        self,
        coordinator: MeshWaldCoordinator,
        entry: ConfigEntry,
        node: str,
        description: MeshWaldSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._node = node
        self._attr_unique_id = f"{entry.entry_id}_{node}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, node)},
            name=f"MeshWald {node}",
            manufacturer="LOONY-TECH / MeshWald",
            model="Meshtastic Sensor-Node",
        )

    @property
    def available(self) -> bool:
        return super().available and self._node in self.coordinator.data

    @property
    def native_value(self) -> Any:
        reading = self.coordinator.data.get(self._node)
        if not reading:
            return None
        return reading.get(self.entity_description.value_key)
