"""Configuration manager for the application."""
import yaml
from pathlib import Path
from loguru import logger

class ConfigManager:
    """Singleton class to manage configuration."""
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from YAML file."""
        if self._config is None:
            try:
                config_path = Path(__file__).parent.parent.parent / 'conf' / 'api_config.yaml'
                with config_path.open('r') as f:
                    self._config = yaml.safe_load(f)
                logger.info("Configuration loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load configuration file: {e}")
                raise Exception(f"Failed to load configuration file: {e}")

    @property
    def config(self):
        """Get the configuration dictionary."""
        return self._config

    def get(self, *keys):
        """Get a configuration value using nested keys."""
        value = self._config
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return None
            value = value[key]
        return value
