# MinIO Storage Integration

This document explains how to use MinIO as a storage option for MedVoice instead of Google Cloud Storage.

## Overview

MinIO is an open-source, high-performance, S3-compatible object storage solution. It's designed to be simple to set up and use, making it ideal for development and testing environments or as a lightweight alternative to cloud storage services.

## Configuration

The application has been configured to use MinIO for storage.

### Environment Variables

Storage configuration is controlled through environment variables:

```
# MinIO configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET_NAME=medvoice-storage
```

### Docker Compose Setup

The project includes a MinIO server in the docker-compose.yml file. The service is configured to:

- Expose the API on port 9000
- Expose the web console on port 9001
- Store data in a persistent volume named `minio_data`
- Use default credentials (minioadmin/minioadmin)

## Implementation Details

The storage implementation uses MinIO as the storage backend, providing S3-compatible object storage functionality.

### Storage Helper Functions

The core storage functionality is in `app/utils/storage_helpers.py`, which provides:

- `init_storage_client()`: Initializes the appropriate storage client
- `upload_file()`: Uploads a file to the configured storage
- `download_file()`: Downloads a file from the configured storage
- `list_files()`: Lists files in the storage
- `extract_path_from_url()`: Extracts the path from a storage URL
- `sort_files_by_datetime()`: Sorts files by datetime in the filename

### Existing API Endpoints

All existing API endpoints in the application work with MinIO storage.

## Web Console Access

When running with Docker Compose, you can access the MinIO web console at:

```
http://localhost:9001
```

Use the default credentials:
- Username: minioadmin
- Password: minioadmin

## Benefits of MinIO

1. **Simplicity**: Easy to set up and use, with no complicated IAM policies
2. **Local Development**: Works well in local development environments
3. **S3 Compatibility**: Uses the same API as Amazon S3, making it easy to switch later
4. **Performance**: High-performance object storage suitable for most needs
5. **Cost**: Free, open-source solution


## Troubleshooting

If you encounter issues with MinIO:

1. Check that the MinIO service is running: `docker ps | grep minio`
2. Verify the MinIO console is accessible at http://localhost:9001
3. Check that the bucket exists in the MinIO console
4. Verify the environment variables are set correctly
5. Look for errors in the application logs