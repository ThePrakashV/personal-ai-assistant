from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Personal AI Assistant"

    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # Short-term memory (Redis / CAG)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    short_term_turns_limit: int = 10

    # Long-term memory (FAISS / MAG)
    embedding_model_name: str = "all-MiniLM-L6-v2"
    faiss_index_path: str = "data/faiss_memory.index"
    faiss_metadata_path: str = "data/faiss_metadata.pkl"
    long_term_top_k: int = 3

    # RAG (documents)
    documents_folder: str = "data/documents"
    rag_index_path: str = "data/rag_index.index"
    rag_metadata_path: str = "data/rag_metadata.pkl"
    chunk_size: int = 500
    chunk_overlap: int = 50
    rag_top_k: int = 3

    # Agent (LangChain / LangGraph)
    agent_max_tool_loops: int = 3

    # Multi-Agent (AutoGen)
    autogen_openai_compat_url: str = "http://localhost:11434/v1"
    autogen_max_turns: int = 6

    # Voice (Whisper STT + TTS)
    whisper_model_size: str = "base"
    voice_temp_folder: str = "data/voice"
    tts_rate: int = 175
    tts_volume: float = 1.0

    # Vision (Ollama vision model)
    vision_model: str = "llava"
    vision_temp_folder: str = "data/vision"

    # Image Generation (Diffusers)
    image_gen_model: str = "runwayml/stable-diffusion-v1-5"
    image_gen_output_folder: str = "data/generated_images"
    image_gen_steps: int = 25
    image_gen_width: int = 512
    image_gen_height: int = 512

    # Monitoring (MLflow / W&B / Dashboard)
    metrics_log_path: str = "data/metrics/requests.jsonl"
    mlflow_db_path: str = "data/mlflow.db"
    mlflow_experiment_name: str = "personal-ai-assistant"
    wandb_project: str = "personal-ai-assistant"
    wandb_mode: str = "offline"  # offline / online / disabled
    dashboard_max_points: int = 2000
    dashboard_refresh_seconds: int = 15

    class Config:
        env_file = ".env"


settings = Settings()