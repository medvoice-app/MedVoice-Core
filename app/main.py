import os, uvicorn, nest_asyncio, requests
from pyngrok import ngrok, conf
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult

from .utils.bucket_helpers import *
from .utils.json_helpers import *
from .llm.rag import RAGSystem_JSON
from .core.google_project_config import *
from .core.app_config import ON_LOCALHOST
from .models.request_enum import *
from .worker import *
from .db.init_db import initialize_all_databases
from .api.v1.api_v1_router import api_router
from .utils.file_helpers import remove_local_file
from .api.v1.endpoints.get.gcloud_storage import get_transcripts_by_user

# Determine if running in Docker
running_in_docker = os.getenv('RUNNING_IN_DOCKER', 'false').lower() == 'true'

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Starting up...")
    if ON_LOCALHOST or not running_in_docker:
        # Only initialize database when in local development
        print("Running in local mode - skipping database initialization")
    else:
        print("Initializing databases...")
        await initialize_all_databases()
    yield
    # Code to run on shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Mounting local directory
app.mount("/static", StaticFiles(directory="/workspace/code/static" if running_in_docker else "static"), name="static")
app.mount("/assets", StaticFiles(directory="/workspace/code/assets" if running_in_docker else "assets"), name="assets")
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

templates = Jinja2Templates(directory=".")

# Include API router
app.include_router(api_router)

@app.get("/")
def index(request: Request):
    """Render the index.html template."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask_v2/{user_id}", tags=["rag-system"])
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

def main():
    """Main entry point for application setup."""
    load_dotenv()
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    ngrok_api_key = os.getenv("NGROK_API_KEY")

    if ngrok_api_key and not ON_LOCALHOST:
        pyngrok_config = conf.PyngrokConfig(
            api_key=ngrok_api_key,
            config_path=os.getenv("NGROK_CONFIG_PATH") if running_in_docker else None,
        )
        conf.set_default(pyngrok_config)
        ngrok_tunnel = ngrok.connect(name=os.getenv("NGROK_TUNNEL", "medvoice_backend"))
        
        print("Public URL:", ngrok_tunnel.public_url)
        nest_asyncio.apply()
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)

main()