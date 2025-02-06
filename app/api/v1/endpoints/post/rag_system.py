import os
import json
from fastapi import APIRouter, HTTPException
from .....models.request_enum import Question
from .....llm.rag import RAGSystem_JSON
from .....utils.file_helpers import remove_local_file
from ..get.gcloud_storage import get_transcripts_by_user

router = APIRouter()

@router.post("/ask_v2/{user_id}", tags=["rag-system"])
async def rag_system_v2(user_id: str, question_body: Question):
    """
    Ask a question to the RAG System.

    - Uses LLM for generating answers.
    - Removes temporary files after processing.
    """
    file_path = f"assets/patients_from_user_{user_id}.json"

    if os.path.exists(file_path):
        remove_local_file(file_path)

    question = question_body.question
    json_data = await get_transcripts_by_user(user_id)

    print(json_data)

    try:
        with open(file_path, "w") as json_file:
            json.dump(json_data, json_file)

        rag_json = RAGSystem_JSON(file_path=file_path)
        answer = await rag_json.handle_question(question)

        remove_local_file(file_path)
        return {"response": answer, "message": "Question answered successfully"}
    except Exception as e:
        if os.path.exists(file_path):
            remove_local_file(file_path)
        raise HTTPException(status_code=500, detail=str(e)) 