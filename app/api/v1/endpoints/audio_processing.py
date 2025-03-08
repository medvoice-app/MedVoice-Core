import tempfile, os, logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from celery.result import AsyncResult
from typing import Optional, List
from ....models.request_enum import AudioExtension, FileExtension, AudioUploadResponse
from ....worker import process_audio_task
from ....utils.storage_helpers import upload_file, check_file_exists
from ....utils.file_helpers import (
    get_file_from_user_upload,
    get_file_from_storage,
    generate_output_filename,
    remove_local_file,
    generate_audio_filename,
)

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/process_upload_audio/{user_id}", response_model=AudioUploadResponse)
async def process_upload_audio(user_id: str, file: UploadFile = File(...)):
    """Handle file upload and process the audio file."""
    temp_path = None
    try:
        # Read file content and get metadata before passing to Celery
        content = await file.read()
        file_metadata = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content)
        }
        
        # Create temporary file
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Create storage path - use the original filename for storage simplicity
        storage_path = f"{file.filename}"
        
        logger.info(f"Uploading file to storage path: {storage_path}")
        
        # Upload file to bucket with original name
        uploaded_url = upload_file(temp_path, storage_path)
        logger.info(f"File uploaded successfully to: {uploaded_url}")
        
        # Verify the file exists in storage before proceeding
        if not await check_file_exists(storage_path):
            raise Exception(f"File verification failed. The file {storage_path} was not found after upload.")
        
        # Start Celery task with the uploaded file information
        task = process_audio_task.delay(
            file_id=storage_path,  # Pass the exact storage path as file_id
            file_extension=os.path.splitext(file.filename)[1][1:],
            user_id=user_id,
            file_name=file.filename,
            file_path=uploaded_url,  # Pass the URL/path in storage
            file_metadata=file_metadata
        )
        logger.info(f"Started processing task with ID: {task.id}")
        
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return AudioUploadResponse(
            message="Audio file uploaded and processing started",
            task_id=str(task.id),
            filename=file.filename
        )
    except Exception as e:
        # Log the detailed error
        logger.error(f"Error processing audio upload: {str(e)}")
        
        # Cleanup temp file if exists
        if temp_path and os.path.exists(temp_path):
            try:
                remove_local_file(temp_path)
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up temporary file: {str(cleanup_error)}")
        
        # Check for S3-specific errors
        error_message = str(e)
        if "S3 operation failed" in error_message or "NoSuchKey" in error_message:
            raise HTTPException(
                status_code=500, 
                detail=f"Storage error: {error_message}"
            )
        
        raise HTTPException(status_code=500, detail=f"Processing error: {error_message}")

@router.post("/upload_audio/{user_id}")
async def upload_audio(user_id: str, file: UploadFile = File(...)):
    """Upload an audio file to storage without processing it."""
    temp_path = None
    try:
        # Read file content
        content = await file.read()
        
        # Create temporary file
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Use original filename for storage
        storage_path = f"{file.filename}"
        
        # Upload file to bucket
        uploaded_url = upload_file(temp_path, storage_path)
        logger.info(f"File uploaded successfully to: {uploaded_url}")
        
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return {
            "message": "Audio file uploaded successfully",
            "filename": file.filename,
            "storage_path": storage_path,
            "url": uploaded_url
        }
    except Exception as e:
        # Cleanup temp file if exists
        if temp_path and os.path.exists(temp_path):
            try:
                remove_local_file(temp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process_transcript")
async def process_transcript(
    transcript: List[str],
    file_id: Optional[str] = None,
    file_extension: Optional[AudioExtension] = AudioExtension.m4a,
    user_id: Optional[str] = None,
    file_name: Optional[str] = None,
):
    """Process and save the transcript of an audio file."""
    try:
        if not transcript:
            raise ValueError("Transcript must be provided")

        file_info = await get_file_from_user_upload(user_id, file_name) if user_id and file_name \
            else await get_file_from_storage(file_id, file_extension) if file_id \
            else None

        if not file_info:
            raise ValueError("Either user_id and file_name or file_id must be provided")

        transcript_text = "\n".join(transcript)
        transcript_file_path = generate_output_filename(transcript, file_info["file_id"], file_info["file_name"])

        upload_file(transcript_file_path, transcript_file_path)
        remove_local_file(file_info["audio_file_path"])
        remove_local_file(transcript_file_path)

        return {"transcript": transcript_text, "file_id": file_info["file_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process_audio_v2/{user_id}")
async def process_audio_v2(
    user_id: str,
    file_id: Optional[str] = None,
    file_extension: Optional[AudioExtension] = AudioExtension.m4a,
    file_name: Optional[str] = None,
):
    """Process an audio file asynchronously."""
    task = process_audio_task.delay(file_id, file_extension, user_id, file_name)
    return {
        "message": "Audio processing started in the background",
        "task_id": task.id,
    }

@router.get("/get_audio_task/{task_id}")
async def get_audio_processing_result(task_id: str):
    """Get the result of an audio processing task."""
    task_result = AsyncResult(task_id)
    if (task_result.ready()):
        result = task_result.get()
        if "error" in result:
            error_msg = result["error"]
            logger.error(f"Task {task_id} failed with error: {error_msg}")
            
            # Extract HTTP status code if present in error message
            status_code = 500
            if error_msg.startswith("500:"):
                error_msg = error_msg[4:].trip()
            
            return {
                "status": "FAILURE",
                "error": error_msg,
                "error_type": "storage_error" if "S3 operation" in error_msg else "processing_error"
            }
        
        return {
            "status": task_result.state,
            "file_id": result["file_id"],
            "llama3_json_output": result["llama3_json_output"],
        }
    return {"status": task_result.state}