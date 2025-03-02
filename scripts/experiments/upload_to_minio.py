from minio import Minio
import os

def upload_blob(endpoint, access_key, secret_key, secure, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the MinIO bucket."""
    # Initialize MinIO client
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )
    
    # Create bucket if it doesn't exist
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"Bucket {bucket_name} created.")
    
    # Determine content type
    content_type = None
    if destination_blob_name.endswith('.mp3'):
        content_type = 'audio/mpeg'
    elif destination_blob_name.endswith('.wav'):
        content_type = 'audio/wav'
    elif destination_blob_name.endswith('.json'):
        content_type = 'application/json'
    
    # Upload file
    client.fput_object(
        bucket_name, 
        destination_blob_name, 
        source_file_name,
        content_type=content_type
    )
    
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
    
    # Construct URL
    protocol = "https" if secure else "http"
    url = f"{protocol}://{endpoint}/{bucket_name}/{destination_blob_name}"
    print(f"URL: {url}")
    
    return url

def download_blob(endpoint, access_key, secret_key, secure, bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the MinIO bucket."""
    # Initialize MinIO client
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )
    
    # Download file
    client.fget_object(bucket_name, source_blob_name, destination_file_name)
    
    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

# Example usage
if __name__ == "__main__":
    # Replace these with your MinIO configuration
    endpoint = "minio:9000"
    access_key = "minioadmin"
    secret_key = "minioadmin"
    secure = False
    bucket_name = "medvoice-storage"
    
    # File paths
    source_file_name = "local/path/to/your/file"
    destination_blob_name = "storage-object-name"
    destination_file_name = "local/path/to/downloaded/file"
    
    # Upload a file to the bucket
    upload_blob(endpoint, access_key, secret_key, secure, bucket_name, source_file_name, destination_blob_name)
    
    # Download a blob from the bucket
    download_blob(endpoint, access_key, secret_key, secure, bucket_name, destination_blob_name, destination_file_name)