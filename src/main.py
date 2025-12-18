import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.tracing import init_tracing
from src.rag import RAGOrchestrator

# Global Orchestrator
orchestrator = None
class StreamRequest(BaseModel):
    user_message: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting EQx Bot API...")
    init_tracing()
    global orchestrator
    orchestrator = RAGOrchestrator()
    yield
    print("🛑 Shutting down...")
    if orchestrator:
        orchestrator.close()

app = FastAPI(title="EQX-Bot V1", lifespan=lifespan)

@app.post("/stream-chat")
async def stream_chat(body: StreamRequest):
    # Get the generator from the orchestrator
    response_generator = orchestrator.process_query(body.user_message)
    
    return StreamingResponse(response_generator, media_type="text/plain")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)