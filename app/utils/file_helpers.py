from fastapi import HTTPException
from typing import List, Dict, Any, Optional, Union
import json, os, requests, datetime, hashlib
import re

from .storage_helpers import upload_file, download_file, extract_path_from_url
from .json_helpers import remove_json_metadata
from ..core.minio_config import *
from ..models.request_enum import AudioExtension
from ..api.v1.endpoints.get.minio_storage import get_audio

# Helper function for getting audio file path
def extract_audio_path(full_url):
    return extract_path_from_url(full_url)

def remove_local_file(file_path):
    if file_path is not None:
        try:
            os.remove(file_path)
            print(f"Successfully removed {file_path}")
        except Exception as e:
            print(f"Error while trying to remove {file_path}: {e}")
    else:
        print("No file path provided, skipping removal.")

async def fetch_and_store_audio(user_id: str, file_name: str):
    try:
        # Initialize file_path
        file_path = os.path.join("audios", os.path.basename(file_name))
        
        # Ensure the audios directory exists
        os.makedirs("audios", exist_ok=True)
        
        # Download the file using our storage helper
        local_file = download_file(file_name, file_path)
        
        print(f"File downloaded successfully to {local_file}")

        # Generate a new filename with metadata
        audio_file = generate_audio_filename(local_file, user_id)
        print(audio_file)
        
        # Upload the file using our storage helper
        upload_file(audio_file['new_file_name'], audio_file['new_file_name'])

        # Clean up the local file
        remove_local_file(audio_file["new_file_name"])

        return {
            "new_file_name": audio_file['new_file_name'], 
            "file_id": audio_file['file_id']
        }
    except Exception as e:
        # Rethrow the exception to be caught by the calling function
        raise e
    
def generate_audio_filename(file_path: str, user_id: str):
    # Ensure the audios/ directory exists
    os.makedirs('audios', exist_ok=True)

    # Get file extension
    file_info = get_file_name_and_extension(file_path)
    patient_name, file_extension = file_info['file_name'], file_info['file_extension']

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create the new file_name with date, original file_name, and user ID
    new_file_name = f'{patient_name}patient_{date_string}date_{user_id}{file_extension}'

    # Hash this new file_name
    file_id = hashlib.sha256(new_file_name.encode('utf-8')).hexdigest()

    # Create the new file_name with hash value, date, original file_name, and user ID
    new_file_name = f'{patient_name}patient_{date_string}date_{file_id}fileID_{user_id}{file_extension}'
    
    # Rename the temporary file
    os.rename(file_path, new_file_name)

    return {"new_file_name": new_file_name, "file_id": file_id}

def generate_output_filename(data: Union[List[str], Dict[str, Any]], file_id: str, user_id: str, file_name: Optional[str] = "transcript") -> str:
    # Ensure 'outputs' directory exists
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # Determine output format based on data type
    if isinstance(data, list):
        file_extension = 'txt'
        data_to_write = '\n'.join(data)
    elif isinstance(data, dict):
        file_extension = 'json'
        
        # Remove JSON metadata
        clean_data = remove_json_metadata(data)

        # Convert the cleaned dictionary to a JSON string
        data_to_write = json.dumps(clean_data, indent=4)  # Use clean_data instead of data

    # Define the local file path
    object_name = f'{file_id}_{file_name}_{user_id}_output.{file_extension}'
    output_file_path = os.path.join('outputs', object_name)

    # Write data to the local file
    with open(output_file_path, 'w') as f:
        f.write(data_to_write)

    print(f"Output saved locally to {output_file_path}")
    
    # Upload to storage and get URL
    file_url = upload_file(output_file_path, object_name)
    
    # Clean up local file
    remove_local_file(output_file_path)
    
    return file_url

# Helper function for file information
def get_file_name_and_extension(file_path):
    # Use os.path.splitext to split the file path into root and extension
    file_name, file_extension = os.path.splitext(file_path)
    # Return the file extension
    return {"file_name": file_name, "file_extension": file_extension}

async def get_file_from_user_upload(user_id: str, file_name: str) -> Dict[str, Any]:
    """Get file information from a user uploaded file."""
    audio_file = await fetch_and_store_audio(user_id, file_name)
    return {
        "file_id": audio_file["file_id"],
        "audio_file_path": None,
        "file_name": file_name
    }

async def get_file_from_storage(file_id: str, file_extension: AudioExtension) -> Dict[str, Any]:
    """Retrieve file information from storage using file_id."""
    file_url = await get_audio(file_id, file_extension)
    audio_file_path = extract_audio_path(file_url)
    file_name = extract_patient_name(audio_file_path)
    return {
        "file_id": file_id,
        "audio_file_path": audio_file_path,
        "file_name": file_name
    }

def extract_patient_name(file_path: str) -> Optional[str]:
    """Extract patient name from file path using regex pattern."""
    pattern = r'(.*?)patient_'
    match = re.search(pattern, file_path)
    if match:
        patient = match.group(1)
        file_name = patient.replace('patient_', '')
        print(f"Patient name: {file_name}")
        return file_name
    return None