import os
import re
import time
import io
import logging
from typing import List, Optional, BinaryIO, Union
from datetime import datetime
from urllib.parse import urlparse

# Import MinIO libraries
from minio import Minio
from minio.error import S3Error

# Import configuration
from ..core.minio_config import minio_config, minio_client

def init_storage_client(max_retries=3, retry_delay=1):
    """
    Get the MinIO client with retry logic if needed.
    Returns a MinIO client and bucket information.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
    """
    global minio_client
    bucket_name = minio_config['bucket_name']
    
    if minio_client is None:
        # If global client initialization failed, try again with retries
        for attempt in range(max_retries):
            try:
                # Initialize MinIO client
                client = Minio(
                    minio_config['endpoint'],
                    access_key=minio_config['access_key'],
                    secret_key=minio_config['secret_key'],
                    secure=minio_config['secure']
                )
                
                # Create bucket if it doesn't exist
                if not client.bucket_exists(bucket_name):
                    client.make_bucket(bucket_name)
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
                        client.set_bucket_policy(bucket_name, policy)
                        logging.info(f"Bucket {bucket_name} created and configured for public access")
                    except Exception as e:
                        logging.warning(f"Could not set public access policy: {e}")
                
                # Update the global client
                minio_client = client
                return {"client": client, "bucket_name": bucket_name}
            
            except Exception as e:
                if attempt < max_retries - 1:
                    logging.warning(f"MinIO connection attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    # Increase delay for next retry (exponential backoff)
                    retry_delay *= 2
                else:
                    logging.error(f"Failed to connect to MinIO after {max_retries} attempts: {e}")
                    raise
    else:
        # Use the global client that was already initialized
        return {"client": minio_client, "bucket_name": bucket_name}

def upload_file(source_file_path: str, destination_blob_name: str = None, data: bytes = None, max_retries=3, retry_delay=1) -> str:
    """
    Upload a file to MinIO with retry logic.
    Returns the public URL to the file.
    
    Args:
        source_file_path: Path to the local file to upload (ignored if data is provided)
        destination_blob_name: Name to give the file in MinIO (default: basename of source_file_path)
        data: Binary data to upload directly (bypasses reading from source_file_path)
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
    """
    if not destination_blob_name and source_file_path:
        destination_blob_name = os.path.basename(source_file_path)
    elif not destination_blob_name:
        raise ValueError("Either source_file_path or destination_blob_name must be provided")
    
    # Determine content type
    content_type = None
    if destination_blob_name.endswith('.mp3'):
        content_type = 'audio/mpeg'
    elif destination_blob_name.endswith('.wav'):
        content_type = 'audio/wav'
    elif destination_blob_name.endswith('.json'):
        content_type = 'application/json'
    
    for attempt in range(max_retries):
        try:
            # Get MinIO client
            storage = init_storage_client()
            client = storage["client"]
            bucket_name = storage["bucket_name"]
            
            # Upload file - choose method based on whether we have data or a file path
            if data is not None:
                # Use put_object with BytesIO for in-memory data
                data_stream = io.BytesIO(data)
                client.put_object(
                    bucket_name,
                    destination_blob_name,
                    data_stream,
                    length=len(data),
                    content_type=content_type
                )
                logging.info(f"Data uploaded to MinIO as {destination_blob_name}")
            else:
                # Use fput_object for file on disk
                client.fput_object(
                    bucket_name, 
                    destination_blob_name, 
                    source_file_path,
                    content_type=content_type
                )
                logging.info(f"File {source_file_path} uploaded to MinIO as {destination_blob_name}")
            
            # For internal container use, use the container name
            protocol = 'http'  # Always use HTTP for internal container communication
            
            # Use the container endpoint for internal URLs
            file_url = f"{protocol}://{minio_config['endpoint']}/{bucket_name}/{destination_blob_name}"
            return file_url
        
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"Upload attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Increase delay for next retry (exponential backoff)
                retry_delay *= 2
            else:
                logging.error(f"Failed to upload file after {max_retries} attempts: {e}")
                raise

def download_file(object_name: str, destination_path: str = None, stream: bool = False, max_retries=3, retry_delay=1) -> Union[str, io.BytesIO]:
    """
    Download a file from MinIO with retry logic.
    
    Args:
        object_name: Name of the object in MinIO to download
        destination_path: Local path to save the file to (default: basename of object_name)
        stream: If True, returns a BytesIO object instead of saving to disk
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
        
    Returns:
        If stream=False: Path to the downloaded file (str)
        If stream=True: BytesIO object containing the file data
    """
    if not destination_path and not stream:
        destination_path = os.path.basename(object_name)
    
    for attempt in range(max_retries):
        try:
            # Get MinIO client
            storage = init_storage_client()
            client = storage["client"]
            bucket_name = storage["bucket_name"]
            
            if stream:
                # Get the object data as a stream
                response = client.get_object(bucket_name, object_name)
                # Read the data into a BytesIO object
                data = io.BytesIO(response.read())
                # Close the response to release resources
                response.close()
                response.release_conn()
                
                logging.info(f"Streamed {object_name} from MinIO")
                return data
            else:
                # Download to a file on disk
                client.fget_object(bucket_name, object_name, destination_path)
                logging.info(f"Downloaded {object_name} from MinIO to {destination_path}")
                return destination_path
        
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"Download attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Increase delay for next retry (exponential backoff)
                retry_delay *= 2
            else:
                logging.error(f"Failed to download file after {max_retries} attempts: {e}")
                raise

def list_files(prefix: str = '', recursive: bool = True, include_url: bool = True, max_retries=3, retry_delay=1) -> List[dict]:
    """
    List files in MinIO with the given prefix and retry logic.
    Returns a list of dictionaries with file information.
    
    Args:
        prefix: Prefix to filter objects by
        recursive: Whether to list objects recursively in subdirectories
        include_url: Whether to include public URLs in the result
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
        
    Returns:
        List of dictionaries containing file metadata
    """
    for attempt in range(max_retries):
        try:
            files = []
            
            # Get MinIO client
            storage = init_storage_client()
            client = storage["client"]
            bucket_name = storage["bucket_name"]
            
            # List objects
            objects = client.list_objects(bucket_name, prefix=prefix, recursive=recursive)
            
            for obj in objects:
                file_info = {
                    "name": obj.object_name,
                    "size": obj.size,
                    "modified": obj.last_modified
                }
                
                # Generate URL if requested (using internal container name)
                if include_url:
                    protocol = 'http'  # Always use HTTP for internal container communication
                    
                    url = f"{protocol}://{minio_config['endpoint']}/{bucket_name}/{obj.object_name}"
                    file_info["url"] = url
                
                files.append(file_info)
            
            return files
            
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"List files attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Increase delay for next retry (exponential backoff)
                retry_delay *= 2
            else:
                logging.error(f"Failed to list files after {max_retries} attempts: {e}")
                raise

def extract_path_from_url(url: str) -> Optional[str]:
    """
    Extract the path/object name from a MinIO URL.
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    
    # The object name is everything after the bucket name in the path
    if len(path_parts) > 2:  # [empty string, bucket name, object name parts...]
        return '/'.join(path_parts[2:])
    return None

def sort_files_by_datetime(files: List[str], pattern=r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})date") -> List[str]:
    """
    Sort files by datetime extracted from filenames.
    """
    # Regular expression to match the date-time in the filename
    regex = re.compile(pattern)
    
    # Function to extract the date-time from a filename and convert it to a datetime object
    def get_datetime_from_filename(filename):
        match = regex.search(filename)
        if match:
            date_time_str = match.group(1)
            date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d_%H-%M-%S")
            return date_time_obj
        else:
            return None
    
    # Extract dates and filter out None values
    date_files = [(file, get_datetime_from_filename(file)) for file in files]
    date_files = [(file, date_time) for file, date_time in date_files if date_time is not None]
    
    # Sort the files based on the date-time
    sorted_files = sorted(date_files, key=lambda x: x[1], reverse=True)
    
    # Return only the files, sorted
    return [file for file, _ in sorted_files]