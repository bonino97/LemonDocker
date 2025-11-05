"""
Configuration manager for environment variables and tool configurations
Supports loading from .env files and secure storage
"""
import os
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from models import Configuration, get_session
import base64


class ConfigManager:
    """
    Manages configuration from multiple sources:
    1. Database (Configuration table)
    2. Environment variables
    3. .env files
    """

    def __init__(self, session: Session = None):
        self.session = session or get_session()
        self._cache = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with priority:
        1. Environment variable
        2. Database
        3. Default value
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Check environment variable
        env_value = os.getenv(key)
        if env_value is not None:
            self._cache[key] = env_value
            return env_value

        # Check database
        config = self.session.query(Configuration).filter_by(key=key).first()
        if config and config.value:
            value = self._decrypt_if_sensitive(config)
            self._cache[key] = value
            return value

        return default

    def set(self, key: str, value: str, description: str = None,
            is_sensitive: bool = False, category: str = "user"):
        """
        Set configuration value in database
        """
        config = self.session.query(Configuration).filter_by(key=key).first()

        if config:
            config.value = self._encrypt_if_sensitive(value, is_sensitive)
            config.description = description or config.description
            config.is_sensitive = is_sensitive
            config.category = category
        else:
            config = Configuration(
                key=key,
                value=self._encrypt_if_sensitive(value, is_sensitive),
                description=description,
                is_sensitive=is_sensitive,
                category=category
            )
            self.session.add(config)

        self.session.commit()

        # Update cache
        self._cache[key] = value

    def get_all_by_category(self, category: str) -> Dict[str, Any]:
        """Get all configurations in a category"""
        configs = self.session.query(Configuration).filter_by(category=category).all()

        return {
            config.key: self._decrypt_if_sensitive(config)
            for config in configs
            if config.value
        }

    def load_env_file(self, file_path: str = ".env"):
        """
        Load configurations from .env file
        """
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Set in environment
                    os.environ[key] = value

    def export_env_file(self, file_path: str = ".env", include_sensitive: bool = False):
        """
        Export configurations to .env file
        """
        configs = self.session.query(Configuration).all()

        with open(file_path, 'w') as f:
            f.write("# LemonDocker Configuration\n")
            f.write(f"# Generated: {os.popen('date').read().strip()}\n\n")

            current_category = None

            for config in sorted(configs, key=lambda x: (x.category, x.key)):
                # Skip sensitive if not included
                if config.is_sensitive and not include_sensitive:
                    continue

                # Category header
                if config.category != current_category:
                    f.write(f"\n# {config.category.upper()}\n")
                    current_category = config.category

                # Write config
                if config.description:
                    f.write(f"# {config.description}\n")

                value = config.value or ""
                if config.is_sensitive and not include_sensitive:
                    value = "***REDACTED***"

                f.write(f"{config.key}={value}\n")

    def get_tool_env(self, tool_name: str) -> Dict[str, str]:
        """
        Get all environment variables required for a specific tool
        """
        from models import Tool

        tool = self.session.query(Tool).filter_by(name=tool_name).first()
        if not tool or not tool.requires_env:
            return {}

        env_vars = {}
        for env_key in tool.requires_env:
            value = self.get(env_key)
            if value:
                env_vars[env_key] = value

        return env_vars

    def validate_pipeline_requirements(self, pipeline_id: int) -> Dict[str, Any]:
        """
        Validate that all required environment variables are set for a pipeline
        """
        from models import Pipeline

        pipeline = self.session.query(Pipeline).get(pipeline_id)
        if not pipeline:
            return {'valid': False, 'error': 'Pipeline not found'}

        missing_vars = []
        warnings = []

        # Check pipeline requirements
        if pipeline.requires_env:
            for env_key in pipeline.requires_env:
                if not self.get(env_key):
                    missing_vars.append(env_key)

        # Check tool requirements
        for step in pipeline.steps:
            if step.tool.requires_env:
                for env_key in step.tool.requires_env:
                    value = self.get(env_key)
                    if not value:
                        if step.required:
                            if env_key not in missing_vars:
                                missing_vars.append(env_key)
                        else:
                            warnings.append(f"{step.tool.name} may not work without {env_key}")

        return {
            'valid': len(missing_vars) == 0,
            'missing_required': missing_vars,
            'warnings': warnings,
            'pipeline': pipeline.name
        }

    def _encrypt_if_sensitive(self, value: str, is_sensitive: bool) -> str:
        """Simple base64 encoding for sensitive values (NOT cryptographically secure)"""
        if is_sensitive and value:
            return base64.b64encode(value.encode()).decode()
        return value

    def _decrypt_if_sensitive(self, config: Configuration) -> str:
        """Decode base64 encoded values"""
        if config.is_sensitive and config.value:
            try:
                return base64.b64decode(config.value.encode()).decode()
            except:
                return config.value
        return config.value

    def create_default_configs(self):
        """Create default configurations"""
        defaults = [
            {
                "key": "RESULTS_BASE_PATH",
                "value": "/opt/results",
                "description": "Base path for storing scan results",
                "category": "system"
            },
            {
                "key": "MAX_PARALLEL_WORKERS",
                "value": "10",
                "description": "Maximum number of parallel Celery workers",
                "category": "system"
            },
            {
                "key": "DEFAULT_TIMEOUT",
                "value": "3600",
                "description": "Default timeout for tool execution (seconds)",
                "category": "system"
            },
            {
                "key": "NUCLEI_TEMPLATES_PATH",
                "value": "/root/nuclei-templates",
                "description": "Path to Nuclei templates directory",
                "category": "tool_config"
            },
            {
                "key": "WORDLIST_PATH",
                "value": "/opt/SecLists",
                "description": "Path to wordlists directory",
                "category": "tool_config"
            },
        ]

        for default in defaults:
            existing = self.session.query(Configuration).filter_by(key=default["key"]).first()
            if not existing:
                config = Configuration(**default)
                self.session.add(config)

        self.session.commit()


# Global instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
