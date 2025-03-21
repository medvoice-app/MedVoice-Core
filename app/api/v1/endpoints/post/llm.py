from typing import Optional

from fastapi import HTTPException, APIRouter
from .....utils.file_helpers import *
from .....utils.json_helpers import *
from .....llm.replicate_models import (
    llama3_generate_medical_json,
    whisper_diarization,
)
from .....llm.llm_helpers import convert_prompt_for_llama3
from .....models.request_enum import Question, SourceType
from .....llm.rag import *

router = APIRouter()

@router.post("/whisper-diarize/")
async def whisper_diarize_endpoint(file_url: str):
    return await whisper_diarize(file_url)

@router.post("/llm-pipeline/")
async def llm_pipeline_audio_to_json_endpoint(
    file_url: str, patient_name: Optional[str] = None
):
    return await llm_pipeline_audio_to_json(file_url, patient_name)

@router.post("/rag-ask/")
async def rag_ask_endpoint(question_body: Question):
    return await rag_system(question_body)

async def rag_system(question_body: Question):
    question = question_body.question
    source_type = question_body.source_type
    try:

        # Assuming RAGSystem_PDF and RAGSystem_JSON are defined elsewhere
        rag_pdf = RAGSystem_PDF("assets/update-28-covid-19-what-we-know.pdf")
        rag_json = RAGSystem_JSON("assets/patients.json")

        if source_type == SourceType.pdf:
            answer = await rag_pdf.handle_question(question)
        elif source_type == SourceType.json:
            answer = await rag_json.handle_question(question)

        # task = llamaguard_task.delay(answer)

        return {
            "response": answer,
            "message": "Question answered successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def whisper_diarize(file_url: str):
    try:
        output = await whisper_diarization(file_url)
        print(pretty_print_json(output))
        prompt_for_llama3 = convert_prompt_for_llama3(output)
        input_transcript = prompt_for_llama3["input_transcript"]

        return input_transcript
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def llm_pipeline_audio_to_json(file_url: str, patient_name: Optional[str] = None):
    try:
        speaker_diarization_json = await whisper_diarization(file_url)

        prompt_for_llama3 = convert_prompt_for_llama3(
            speaker_diarization_json, patient_name
        )

        # Pass the prompt directly - it already contains the transcript and context
        llama3_json_output = await llama3_generate_medical_json(
            prompt_for_llama3["prompt"]
        )

        print(pretty_print_json(llama3_json_output))
        return llama3_json_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
