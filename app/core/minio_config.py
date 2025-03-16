from minio import Minio
import logging
from app.core.config_loader import config

# Create backward compatibility dictionary for existing code
minio_config = {
    "endpoint": config.minio.endpoint,
    "external_endpoint": config.minio.external_endpoint, 
    "access_key": config.minio.access_key,
    "secret_key": config.minio.secret_key,
    "secure": config.minio.secure,
    "bucket_name": config.minio.bucket_name
}

# Global MinIO client
minio_client = None

def get_minio_client():
    global minio_client
    if minio_client is None:
        try:
            minio_client = Minio(
                config.minio.endpoint,
                access_key=config.minio.access_key,
                secret_key=config.minio.secret_key,
                secure=config.minio.secure
            )
        except Exception as e:
            logging.error(f"Failed to initialize MinIO client: {e}")
    return minio_client

# Initialize MinIO client at module level
try:
    minio_client = Minio(
        config.minio.endpoint,
        access_key=config.minio.access_key,
        secret_key=config.minio.secret_key,
        secure=config.minio.secure
    )
    
    # Ensure the bucket exists
    bucket_name = config.minio.bucket_name
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        # Set bucket policy for public access if required
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                    }
                ]
            }
            minio_client.set_bucket_policy(bucket_name, policy)
            logging.info(f"Bucket {bucket_name} created and configured for public access")
        except Exception as e:
            logging.warning(f"Could not set public access policy: {e}")
    
    logging.info("MinIO client initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize MinIO client: {e}")
    minio_client = None