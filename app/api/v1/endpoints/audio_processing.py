import tempfile, os
from fastapi import APIRouter, UploadFile, File, HTTPException
from celery.result import AsyncResult
from typing import Optional, List
from ....models.request_enum import AudioExtension, FileExtension, AudioUploadResponse
from ....worker import process_audio_task
from ....utils.file_helpers import (
    get_file_from_user_upload,
    get_file_from_storage,
    generate_output_filename,
    remove_local_file,
    upload_file_to_bucket
)

router = APIRouter()

@router.post("/process_upload_audio/{user_id}", response_model=AudioUploadResponse)
async def process_upload_audio(user_id: str, file: UploadFile = File(...)):
    """Handle file upload and process the audio file."""
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

        # Start Celery task with file path instead of UploadFile
        task = process_audio_task.delay(
            file_id=None,
            file_extension=os.path.splitext(file.filename)[1][1:],
            user_id=user_id,
            file_name=file.filename,
            file_path=temp_path,  # Pass path instead of file object
            file_metadata=file_metadata  # Pass metadata separately
        )
        
        return AudioUploadResponse(
            message="Audio file uploaded and processing started",
            task_id=str(task.id),
            filename=file.filename
        )
    except Exception as e:
        # Cleanup temp file if exists
        if 'temp_path' in locals():
            try:
                os.remove(temp_path)
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

        upload_file_to_bucket(transcript_file_path, transcript_file_path)
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
            return {"status": task_result.state, "error": result["error"]}
        return {
            "status": task_result.state,
            "file_id": result["file_id"],
            "llama3_json_output": result["llama3_json_output"],
        }
    return {"status": task_result.state}