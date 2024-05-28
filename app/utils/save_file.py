import os
import datetime
import hashlib
import json
from typing import List, Dict, Any, Optional

def save_audio(file_path: str, user_id: str):
    # Ensure the audios/ directory exists
    os.makedirs('audios', exist_ok=True)

    temp_audio_path = file_path

    # Get file extension
    file_info = get_file_info(temp_audio_path)
    file_name, file_extension = file_info['file_name'], file_info['file_extension']

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time as a string
    date_string = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create the new file_name with date, original file_name, and user ID
    new_file_name = f'{file_name}patient_{date_string}date_{user_id}{file_extension}'

    # Hash this new file_name
    file_id = hashlib.sha256(new_file_name.encode('utf-8')).hexdigest()

    # Create the new file_name with hash value, date, original file_name, and user ID
    new_file_name = f'{file_name}patient_{date_string}date_{file_id}fileID_{user_id}{file_extension}'
    
    # Rename the temporary file
    # new_audio_path = os.path.join('audios', new_file_name)
    os.rename(file_path, new_file_name)

    return {"new_file_name": new_file_name, "file_id": file_id}

def save_json_to_text(json_output: List[Dict[str, Any]], file_id: str, file_name: Optional[str] = None) -> str:
    # Ensure 'outputs' directory exists
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # Convert each dictionary in 'json_output' to a string
    json_output_text = '\n'.join(json.dumps(item) for item in json_output)

    # Define the full file path
    output_file_path = os.path.join('outputs', f'{file_id}_{file_name}json_output.txt')

    # Write 'json_output' to a file in the 'outputs' directory
    with open(output_file_path, 'w') as f:
        f.write(json_output_text)

    print(f"'json_output' saved to {output_file_path}")

    return output_file_path

def save_strings_to_text(strings_output: List[str], file_id: str, file_name: Optional[str] = None) -> str:
    # Ensure 'outputs' directory exists
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # Convert the list of strings to a single string
    strings_output_text = '\n'.join(strings_output)

    # Define the full file path
    output_file_path = os.path.join('outputs', f'{file_id}_{file_name}strings_output.txt')

    # Write 'strings_output' to a file in the 'outputs' directory
    with open(output_file_path, 'w') as f:
        f.write(strings_output_text)

    print(f"'strings_output' saved to {output_file_path}")

    return output_file_path

def save_json_output(json_output: List[Dict[str, Any]], file_id: str, file_name: str):
    # Ensure 'outputs' directory exists
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    # Define the full file path
    output_file_path = os.path.join('outputs', f'{file_id}_{file_name}_json_output.json')

    # Write the json_output to the file
    with open(output_file_path, 'w') as f:
        json.dump(json_output, f)

    print(f"JSON output saved to {output_file_path}")

    return output_file_path

# Helper function for audio
def get_file_info(file_path):
    # Use os.path.splitext to split the file path into root and extension
    file_name, file_extension = os.path.splitext(file_path)
    # Return the file extension
    return {"file_name": file_name, "file_extension": file_extension}

