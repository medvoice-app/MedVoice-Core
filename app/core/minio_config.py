from dotenv import load_dotenv
import os
from minio import Minio
from minio.error import S3Error
import logging

# Load environment variables from .env file
load_dotenv()

# MinIO configuration
minio_config = {
    "endpoint": os.getenv("MINIO_ENDPOINT", "minio:9000"),  # Use container name for Docker
    "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    "secure": False,  # Force HTTP for Docker environment
    "bucket_name": os.getenv("MINIO_BUCKET_NAME", "medvoice-storage"),
    "external_endpoint": os.getenv("MINIO_EXTERNAL_ENDPOINT", "localhost:9000")  # For external URLs
}

# Global MinIO client
minio_client = None

def get_minio_client():
    """
    Returns the global MinIO client instance.
    If the client hasn't been initialized yet, it initializes it.
    
    Returns:
        A configured MinIO client instance
    """
    global minio_client
    
    if not minio_client:
        # Initialize the client if it doesn't exist yet
        from minio import Minio
        
        minio_client = Minio(
            minio_config['endpoint'],
            access_key=minio_config['access_key'],
            secret_key=minio_config['secret_key'],
            secure=minio_config['secure']
        )
        
        # Configure the client to include bucket information
        minio_client._get_config = lambda: {"bucket_name": minio_config['bucket_name']}
    
    return minio_client

# Initialize MinIO client at module level
try:
    minio_client = Minio(
        minio_config["endpoint"],
        access_key=minio_config["access_key"],
        secret_key=minio_config["secret_key"],
        secure=minio_config["secure"]
    )
    
    # Ensure the bucket exists
    bucket_name = minio_config["bucket_name"]
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