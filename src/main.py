from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
import random
from pydantic import BaseModel
import asyncio


class StreamRequest(BaseModel):
    user_message: str
    temperature: float = 0.7

# Initialize the app
app = FastAPI(title="EQX-Bot V1")


# async def llm_generator_test():
#     message = "You are absolutely right. I apologize."
#     for word in message.split():
#         yield f"{word} "
#         # Simulate "thinking" time between tokens
#         await asyncio.sleep(1.2)

# # 2. The Endpoint
# @app.get("/stream-chat")
# async def stream_chat():
#     # We pass the generator function to StreamingResponse
#     return StreamingResponse(llm_generator_test(), media_type="text/plain")


# 2. Generator uses the Pydantic data
async def llm_generator_test(request: StreamRequest):
    # In reality, you'd send request.user_message to OpenAI here
    response_content = f"This was your message: {request.user_message}"
    
    for word in response_content.split():
        yield f"{word} "
        await asyncio.sleep(0.21)

# 3. Endpoint receives Pydantic model
@app.post("/stream-chat")
async def stream_chat(body: StreamRequest):
    return StreamingResponse(llm_generator_test(body), media_type="text/plain")


@app.get("/health")
async def health_check():
    """Simple check to see if the server is running."""
    return {"status": "ok", "system": "prototype-v1"}








if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)