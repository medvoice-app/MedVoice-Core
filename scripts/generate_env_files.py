#!/usr/bin/env python3
import os
import sys
import yaml

# Add project root to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config_loader import ConfigLoader

def generate_service_env_files():
    """Generate environment files for Docker services from config files"""
    
    # Load configurations using the existing config loader
    loader = ConfigLoader()
    config = loader.settings
    
    # Create env directory if it doesn't exist
    env_dir = os.path.join(os.path.dirname(__file__), '..', 'env')
    os.makedirs(env_dir, exist_ok=True)
    
    # Generate web service environment file
    web_env_path = os.path.join(env_dir, 'web.env')
    with open(web_env_path, 'w') as f:
        f.write(f"REDIS_URL=redis://redis:6379/0\n")
        f.write(f"RUNNING_IN_DOCKER=true\n")
        f.write(f"APP_ENVIRONMENT={os.getenv('APP_ENVIRONMENT', 'local')}\n")
        f.write(f"MINIO_ENDPOINT={config.minio.endpoint}\n")
        f.write(f"MINIO_EXTERNAL_ENDPOINT={config.minio.external_endpoint}\n")
        f.write(f"MINIO_ACCESS_KEY={config.minio.access_key}\n")
        f.write(f"MINIO_SECRET_KEY={config.minio.secret_key}\n")
        f.write(f"MINIO_SECURE={'true' if config.minio.secure else 'false'}\n")
        f.write(f"MINIO_BUCKET_NAME={config.minio.bucket_name}\n")
    
    # Generate worker service environment file
    worker_env_path = os.path.join(env_dir, 'worker.env')
    with open(worker_env_path, 'w') as f:
        f.write(f"REDIS_URL=redis://redis:6379/0\n")
        f.write(f"MINIO_ENDPOINT={config.minio.endpoint}\n")
        f.write(f"MINIO_EXTERNAL_ENDPOINT={config.minio.external_endpoint}\n")
        f.write(f"MINIO_ACCESS_KEY={config.minio.access_key}\n")
        f.write(f"MINIO_SECRET_KEY={config.minio.secret_key}\n")
        f.write(f"MINIO_SECURE={'true' if config.minio.secure else 'false'}\n")
        f.write(f"MINIO_BUCKET_NAME={config.minio.bucket_name}\n")
    
    # Generate MinIO service environment file  
    minio_env_path = os.path.join(env_dir, 'minio.env')
    with open(minio_env_path, 'w') as f:
        f.write(f"MINIO_ROOT_USER={config.minio.access_key}\n")
        f.write(f"MINIO_ROOT_PASSWORD={config.minio.secret_key}\n")
    
    print(f"Environment files generated successfully in {env_dir}")

if __name__ == "__main__":
    generate_service_env_files()
