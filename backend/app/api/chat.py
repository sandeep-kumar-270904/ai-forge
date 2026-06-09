from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from ..ai.agent import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()

@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    await manager.connect(websocket)
    messages = []
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_input = payload.get("message")
            
            if not user_input:
                continue
                
            messages.append(HumanMessage(content=user_input))
            
            final_response = ""
            async for event in agent_app.astream_events({"messages": messages, "workspace_id": workspace_id}, version="v2"):
                kind = event["event"]
                
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk:
                        if isinstance(chunk, str):
                            final_response += chunk
                            await websocket.send_json({"type": "stream", "content": chunk})
                        elif isinstance(chunk, list):
                             for c in chunk:
                                 if "text" in c:
                                     final_response += c["text"]
                                     await websocket.send_json({"type": "stream", "content": c["text"]})
            
            messages.append(AIMessage(content=final_response))
            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
