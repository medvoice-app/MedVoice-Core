# MedVoice Core System

MedVoice is an AI-powered healthcare documentation system that automatically generates clinical documentation from doctor-patient conversations.

## Project Demo

Watch a demonstration of the MedVoice-FastAPI project:

[![Demo Video](https://img.youtube.com/vi/euxRibBCnwM/0.jpg)](https://www.youtube.com/watch?v=euxRibBCnwM)

## Project Architecture

```mermaid
flowchart TB
    subgraph "Client Layer"
        MobileApp["Mobile Application (Doctor Interface)"]
    end

    subgraph "API Layer"
        FastAPI["FastAPI Backend (8000)"]
        APIEndpoints["API Endpoints (/api/v1/*)"]
        Middleware["Authentication Middleware"]
    end

    subgraph "Core Services"
        AudioProcessor["Audio Processing (Whisper)"]
        LLMService["LLM Services (Llama3)"]
        RAGSystem["RAG System (Embeddings)"]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database)]
        VectorStore[(PGVector Embeddings)]
        MinIO[(MinIO Object Storage)]
    end

    subgraph "Worker Layer"
        Worker["Async Workers"]
    end

    MobileApp -->|HTTP/REST| FastAPI
    FastAPI --> APIEndpoints
    APIEndpoints --> Middleware
    
    Middleware -->|Process Audio| AudioProcessor
    Middleware -->|Generate Documentation| LLMService
    Middleware -->|Retrieve Context| RAGSystem

    AudioProcessor -->|Store Audio| MinIO
    AudioProcessor -->|Transcribe| LLMService
    LLMService -->|Store Results| PostgreSQL
    RAGSystem -->|Query Vectors| VectorStore
    
    Worker -->|Background Tasks| AudioProcessor
    Worker -->|Background Tasks| LLMService
    
    PostgreSQL -->|Data Access| Middleware
    MinIO -->|File Access| Middleware
    VectorStore -->|Embeddings| RAGSystem

    classDef primary fill:#3498db,stroke:#2980b9,color:white
    classDef secondary fill:#2ecc71,stroke:#27ae60,color:white
    classDef storage fill:#e74c3c,stroke:#c0392b,color:white
    classDef worker fill:#f39c12,stroke:#d35400,color:white

    class MobileApp,FastAPI,APIEndpoints primary
    class AudioProcessor,LLMService,RAGSystem,Middleware secondary
    class PostgreSQL,VectorStore,MinIO storage
    class Worker worker
```

## Project Structure

```
MedVoice-FastAPI/
├── app/                    # Main application code
│   ├── api/                # API endpoints
│   │   └── v1/             # API version 1
│   ├── core/               # Core configuration
│   ├── crud/               # Database CRUD operations
│   ├── db/                 # Database connection and models
│   ├── llm/                # LLM integration code
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   └── utils/              # Utility functions
├── assets/                 # Static assets
├── audios/                 # Audio file storage
├── docker/                 # Docker configuration files
├── docs/                   # Documentation
├── outputs/                # Output file storage
├── scripts/                # Utility scripts
└── static/                 # Static frontend files
    └── js/                 # JavaScript files
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Make
- Git

### Local Development Setup

1. **Clone the repository:**
   ```shell
   git clone https://github.com/MedVoice-RMIT-CapStone-2024/MedVoice-FastAPI.git
   cd MedVoice-FastAPI
   ```

2. **Verify dependencies:**
   ```shell
   make check
   ```

3. **Set up environment:**
   ```shell
   make setup
   ```
   This command creates a Python virtual environment, installs dependencies, and generates a default `.env` file.

4. **Start the application:**
   ```shell
   make up
   ```
   For GPU acceleration (if available):
   ```shell
   make GPU=true up
   ```

5. **Access the application:**
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/docs
   - MinIO Storage interface: http://127.0.0.1:9001
   - Flower Dashboard: http://localhost:5557/workers

## Additional Configuration

### Environment Variables

The basic configuration is handled automatically, but you can modify the following variables in your `.env` file if needed:

```env
# MinIO configuration
MINIO_ENDPOINT=minio:9000
MINIO_EXTERNAL_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET_NAME=medvoice-storage

# For AI model integration
REPLICATE_API_TOKEN=your-replicate-api-token
HF_ACCESS_TOKEN=your-hugging-face-api-token

# Ollama configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Remote Access Configuration (Optional)

For remote access using ngrok:

1. Update `app/core/app_config.py`:
   ```python
   ON_LOCALHOST = 0
   ```

2. Configure ngrok in your `.env` file:
   ```env
   NGROK_AUTH_TOKEN=your-auth-token
   NGROK_API_KEY=your-api-key
   NGROK_EDGE=your-edge-label
   NGROK_TUNNEL=your-tunnel-name
   ```

3. Generate ngrok configuration:
   ```shell
   make ngrok
   ```

## Utility Commands

- Stop the application:
  ```shell
  make down
  ```

- Export dependencies:
  ```shell
  make export
  ```

- Import dependencies:
  ```shell
  make import
  ```

## License

This project is licensed under the [GNU GENERAL PL License](LICENSE).

## Reference
- [How to install NVIDIA drivers on Ubuntu](https://linuxconfig.org/how-to-install-the-nvidia-drivers-on-ubuntu-22-04)