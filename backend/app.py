from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
import uuid

import os
from dotenv import load_dotenv

load_dotenv()

from agent.agent import agent

app = FastAPI(title="AutoStream AI Sales Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
        
    config = {"configurable": {"thread_id": request.session_id}}
    
    
    
    try:
        response_state = agent.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
    raw_content = response_state["messages"][-1].content
    if isinstance(raw_content, list):
        final_output = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in raw_content])
    else:
        final_output = str(raw_content)
        
    
    debug_state = {
        "intent": response_state.get("intent"),
        "name": response_state.get("name"),
        "email": response_state.get("email"),
        "platform": response_state.get("platform")
    }
    
    return {"reply": final_output, "debug_state": debug_state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
