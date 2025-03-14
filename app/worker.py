import os, re, asyncio
from typing import Optional, Dict, Any, Tuple
from celery import Celery
from fastapi import HTTPException, UploadFile

from .utils.storage_helpers import *
from .utils.file_helpers import *
from .utils.json_helpers import *
from .core.minio_config import minio_config
from .models.request_enum import *

# API Router
from .api.v1.endpoints.post.llm import *
from .api.v1.endpoints.get.minio_storage import *

# In app/worker.py
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(__name__, broker=redis_url, backend=redis_url)

# Add Celery configuration
celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Autodiscover tasks in the 'app' package, specifically looking in 'main.py'
celery_app.autodiscover_tasks()


async def handle_uploaded_file_case(user_id: str, file_path: str, file_metadata: dict) -> Tuple[str, str, str, str]:
    """Handle the case when a file is uploaded directly."""
    try:
        audio_file = await fetch_and_store_audio(user_id, file_metadata["filename"])
        file_id, audio_file_path = audio_file["file_id"], audio_file["new_file_name"]
        
        # Construct MinIO URL
        if minio_config['secure']:
            protocol = 'https'
        else:
            protocol = 'http'
        file_url = f"{protocol}://{minio_config['endpoint']}/{minio_config['bucket_name']}/{audio_file_path}"
        
        patient_name = get_file_name_and_extension(file_metadata["filename"])["file_name"]
        
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return file_id, audio_file_path, file_url, patient_name
    except Exception as e:
        # Ensure cleanup on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

async def handle_file_id_case(file_id: str, file_extension: AudioExtension) -> Tuple[str, str, str]:
    """Handle the case when a file_id is provided."""
    file_url = await get_audio(file_id, file_extension)
    audio_file_path = extract_audio_path(file_url)
    
    pattern = r"/(.*?)patient_"
    match = re.search(pattern, audio_file_path)
    patient_name = None
    if match:
        patient_name = match.group(1)
        
    return audio_file_path, file_url, patient_name

async def handle_user_file_case(user_id: str, file_name: str) -> Tuple[str, str, str, str]:
    """Handle the case when user_id and file_name are provided."""
    audio_file = await fetch_and_store_audio(user_id, file_name)
    file_id, audio_file_path = audio_file["file_id"], audio_file["new_file_name"]
    
    # Construct MinIO URL using internal container endpoint
    protocol = 'http'  # Always use HTTP for internal container communication
    file_url = f"{protocol}://{minio_config['endpoint']}/{minio_config['bucket_name']}/{audio_file_path}"
    
    patient_name = get_file_name_and_extension(file_name)["file_name"]
    
    return file_id, audio_file_path, file_url, patient_name

async def process_audio_output(llama3_json_output: Dict[str, Any], file_id: str, user_id: str, 
                             file_name: str, audio_file_path: str) -> Dict[str, Any]:
    """Process and save the audio output."""
    # Generate and upload output file - generate_output_filename now handles the upload
    transcript_url = generate_output_filename(
        llama3_json_output, file_id, user_id, file_name
    )
    
    # Clean up any remaining local files
    remove_local_file(audio_file_path)
    
    return {
        "file_id": file_id, 
        "llama3_json_output": llama3_json_output,
        "transcript_url": transcript_url
    }

async def process_audio_background(
    file_id: Optional[str] = None,
    file_extension: Optional[AudioExtension] = AudioExtension.m4a,
    user_id: Optional[str] = None,
    file_name: Optional[str] = None,
    file_path: Optional[str] = None,
    file_metadata: Optional[dict] = None,
):
    """Main audio processing function."""
    try:
        # Initialize variables
        patient_name = None
        audio_file_path = None
        file_url = None
        
        # Handle different input cases
        if user_id and file_path and file_metadata:
            file_id, audio_file_path, file_url, patient_name = await handle_uploaded_file_case(user_id, file_path, file_metadata)
        elif file_id:
            audio_file_path, file_url, patient_name = await handle_file_id_case(file_id, file_extension)
            file_name = patient_name.replace("patient_", "") if patient_name else None
        elif user_id and file_name:
            file_id, audio_file_path, file_url, patient_name = await handle_user_file_case(user_id, file_name)

        # Process audio with LLM
        llama3_json_output = await llm_pipeline_audio_to_json(file_url, patient_name)
        
        # Handle output and cleanup
        return await process_audio_output(llama3_json_output, file_id, user_id, file_name, audio_file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@celery_app.task(name="process_audio_task")
def process_audio_task(
    file_id: Optional[str] = None,
    file_extension: str = "m4a",
    user_id: Optional[str] = None,
    file_name: Optional[str] = None,
    file_path: Optional[str] = None,
    file_metadata: Optional[dict] = None,
):
    try:
        # Run the async function in an event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            process_audio_background(
                file_id=file_id,
                file_extension=file_extension,
                user_id=user_id,
                file_name=file_name,
                file_path=file_path,
                file_metadata=file_metadata
            )
        )
        return result
    except Exception as e:
        return {"error": str(e)}
