from contextlib import asynccontextmanager
from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from .faq_data import load_faq_dataset
from .openai_writer import OpenAIResponseWriter
from .schemas import ChatRequest, ChatResponse
from .service import StrideChatService


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend-legacy"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = StrideChatService(
        load_faq_dataset(),
        writer=OpenAIResponseWriter(),
    )
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Stride Chatbot API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip().rstrip("/") for origin in os.getenv(
            "ALLOWED_ORIGINS", "http://127.0.0.1:5174,http://localhost:5174"
        ).split(",") if origin.strip()],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "stride-chatbot"}

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(payload: ChatRequest) -> ChatResponse:
        return await run_in_threadpool(app.state.service.process_message, payload.message, payload.context)

    @app.get("/", include_in_schema=False)
    async def home() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    return app


app = create_app()
