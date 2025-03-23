import os
import yaml
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Define configuration models
class AppConfig(BaseModel):
    insert_mock_data: int = 0
    on_localhost: int = 1
    rag_sys: int = 1

class MinioConfig(BaseModel):
    endpoint: str = "minio:9000"
    external_endpoint: str = "localhost:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    secure: bool = False
    bucket_name: str = "medvoice-storage"

class OllamaConfig(BaseModel):
    base_url: str = "http://host.docker.internal:11434"

class TokensConfig(BaseModel):
    replicate: str = ""
    huggingface: str = ""

class NgrokConfig(BaseModel):
    auth_token: str = ""
    api_key: str = ""
    edge: str = ""
    tunnel: str = ""

class AppSettings(BaseModel):
    app: AppConfig
    minio: MinioConfig
    ollama: OllamaConfig
    tokens: TokensConfig = TokensConfig()
    ngrok: NgrokConfig = NgrokConfig()


class ConfigLoader:
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        self.settings = self._load_config()

    def _load_yaml_file(self, filename: str) -> Optional[Dict[str, Any]]:
        filepath = os.path.join(self.config_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as file:
                    return yaml.safe_load(file)
            except Exception as e:
                logger.error(f"Error loading {filepath}: {e}")
                return None
        return None

    def _load_config(self) -> AppSettings:
        # Load default config
        default_config = self._load_yaml_file("default.yaml") or {}
        
        # Determine environment from environment variable
        env = os.getenv("APP_ENVIRONMENT", "local")
        
        # Load environment-specific config
        env_config = self._load_yaml_file(f"{env}.yaml") or {}
        
        # Merge configs with environment config taking precedence
        merged_config = self._deep_merge(default_config, env_config)
        
        # Override with environment variables if they exist
        self._override_from_env(merged_config)
        
        # Add tokens and ngrok config from environment variables
        merged_config["tokens"] = self._load_tokens_from_env()
        merged_config["ngrok"] = self._load_ngrok_from_env()
        
        # Convert to Pydantic model
        return AppSettings(**merged_config)

    def _deep_merge(self, source: Dict[str, Any], destination: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries with destination values taking precedence."""
        for key, value in destination.items():
            if key in source and isinstance(source[key], dict) and isinstance(value, dict):
                source[key] = self._deep_merge(source[key], value)
            else:
                source[key] = value
        return source
    
    def _load_tokens_from_env(self) -> Dict[str, str]:
        """Load API tokens exclusively from environment variables."""
        return {
            "replicate": os.getenv("REPLICATE_API_TOKEN", ""),
            "huggingface": os.getenv("HF_ACCESS_TOKEN", "")
        }
    
    def _load_ngrok_from_env(self) -> Dict[str, str]:
        """Load Ngrok configuration exclusively from environment variables."""
        return {
            "auth_token": os.getenv("NGROK_AUTH_TOKEN", ""),
            "api_key": os.getenv("NGROK_API_KEY", ""),
            "edge": os.getenv("NGROK_EDGE", ""),
            "tunnel": os.getenv("NGROK_TUNNEL", "")
        }

    def _override_from_env(self, config: Dict[str, Any]) -> None:
        """Override configuration with environment variables if they exist."""
        # App config overrides
        if os.getenv("INSERT_MOCK_DATA") is not None:
            config.setdefault("app", {})["insert_mock_data"] = int(os.getenv("INSERT_MOCK_DATA"))
        if os.getenv("ON_LOCALHOST") is not None:
            config.setdefault("app", {})["on_localhost"] = int(os.getenv("ON_LOCALHOST"))
        if os.getenv("RAG_SYS") is not None:
            config.setdefault("app", {})["rag_sys"] = int(os.getenv("RAG_SYS"))

        # MinIO config overrides
        if os.getenv("MINIO_ENDPOINT"):
            config.setdefault("minio", {})["endpoint"] = os.getenv("MINIO_ENDPOINT")
        if os.getenv("MINIO_EXTERNAL_ENDPOINT"):
            config.setdefault("minio", {})["external_endpoint"] = os.getenv("MINIO_EXTERNAL_ENDPOINT")
        if os.getenv("MINIO_ACCESS_KEY"):
            config.setdefault("minio", {})["access_key"] = os.getenv("MINIO_ACCESS_KEY")
        if os.getenv("MINIO_SECRET_KEY"):
            config.setdefault("minio", {})["secret_key"] = os.getenv("MINIO_SECRET_KEY")
        if os.getenv("MINIO_SECURE") is not None:
            config.setdefault("minio", {})["secure"] = os.getenv("MINIO_SECURE").lower() == "true"
        if os.getenv("MINIO_BUCKET_NAME"):
            config.setdefault("minio", {})["bucket_name"] = os.getenv("MINIO_BUCKET_NAME")

        # Ollama config overrides
        if os.getenv("OLLAMA_BASE_URL"):
            config.setdefault("ollama", {})["base_url"] = os.getenv("OLLAMA_BASE_URL")


# Create a global instance
config = ConfigLoader().settings

# Backward compatibility with old app_config structure
INSERT_MOCK_DATA = config.app.insert_mock_data
ON_LOCALHOST = config.app.on_localhost
RAG_SYS = config.app.rag_sys
