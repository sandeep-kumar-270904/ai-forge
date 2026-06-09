from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
import json
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..ai.agent import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage
from ..core.config import settings
from ..core.database import SessionLocal
from ..models.user import User
from ..models.workspace import Workspace

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

async def get_user_from_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
        if token_data is None:
            return None
    except (jwt.JWTError, ValidationError):
        return None
    result = await db.execute(select(User).filter(User.id == token_data))
    return result.scalars().first()

@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    workspace_id: str, 
    token: str = Query(None)
):
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with SessionLocal() as db:
        user = await get_user_from_token(token, db)
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        result = await db.execute(select(Workspace).filter(
            Workspace.id == workspace_id, 
            Workspace.tenant_id == user.tenant_id
        ))
        workspace = result.scalars().first()
        
        if not workspace:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await manager.connect(websocket)
        messages = []
        
        try:
            while True:
                data = await websocket.receive_text()
                payload = json.loads(data)
                user_input = payload.get("message")
                
                if not user_input:
                    continue
                    
                if len(user_input) > 1000:
                    await websocket.send_json({"type": "stream", "content": "Error: Input exceeds maximum length of 1000 characters."})
                    await websocket.send_json({"type": "done"})
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
