"""Constants for the MeshWald integration."""
import logging
from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "meshwald"
LOGGER = logging.getLogger(__package__)

CONF_BASE_URL = "base_url"
CONF_API_KEY = "api_key"

DEFAULT_BASE_URL = "https://meshwald.de"
SCAN_INTERVAL = timedelta(seconds=60)
REQUEST_TIMEOUT = 10

PLATFORMS = [Platform.SENSOR]
