import os
import json
import threading
from typing import Dict, List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for bots, clients, webhooks, and logs
bots: Dict[str, Dict] = {}
clients: Dict[str, List[str]] = {}  # client_id -> list of bot_ids
webhooks: Dict[str, List[str]] = {}  # bot_id -> list of webhook URLs
logs: Dict[str, List[Dict]] = {}  # bot_id -> list of log entries

class BotConfig(BaseModel):
    bot_id: str
    name: str
    description: str
    personality: str
    tools: List[str]
    enabled: bool = True

class WebhookConfig(BaseModel):
    bot_id: str
    webhook_url: str

@app.post("/bots/")
async def create_or_update_bot(config: BotConfig):
    bots[config.bot_id] = config.dict()
    if config.bot_id not in logs:
        logs[config.bot_id] = []
    return {"message": "Bot created/updated successfully"}

@app.get("/bots/{bot_id}")
async def get_bot(bot_id: str):
    bot = bots.get(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    return bot

@app.post("/clients/{client_id}/enable_bot/{bot_id}")
async def enable_bot_for_client(client_id: str, bot_id: str):
    if bot_id not in bots:
        raise HTTPException(status_code=404, detail="Bot not found")
    clients.setdefault(client_id, [])
    if bot_id not in clients[client_id]:
        clients[client_id].append(bot_id)
    return {"message": f"Bot {bot_id} enabled for client {client_id}"}

@app.get("/clients/{client_id}/bots")
async def get_enabled_bots_for_client(client_id: str):
    bot_ids = clients.get(client_id, [])
    return {"bots": [bots[bot_id] for bot_id in bot_ids if bot_id in bots]}

@app.post("/webhooks/")
async def add_webhook(config: WebhookConfig):
    if config.bot_id not in bots:
        raise HTTPException(status_code=404, detail="Bot not found")
    webhooks.setdefault(config.bot_id, [])
    if config.webhook_url not in webhooks[config.bot_id]:
        webhooks[config.bot_id].append(config.webhook_url)
    return {"message": "Webhook added successfully"}

@app.get("/webhooks/{bot_id}")
async def get_webhooks(bot_id: str):
    return {"webhooks": webhooks.get(bot_id, [])}

@app.post("/logs/{bot_id}")
async def add_log(bot_id: str, log_entry: Dict):
    if bot_id not in bots:
        raise HTTPException(status_code=404, detail="Bot not found")
    logs.setdefault(bot_id, [])
    logs[bot_id].append(log_entry)
    return {"message": "Log added"}

@app.get("/logs/{bot_id}")
async def get_logs(bot_id: str):
    return {"logs": logs.get(bot_id, [])}

# Placeholder for training data processing
@app.post("/training/{bot_id}")
async def upload_training_data(bot_id: str, files: List[UploadFile] = File(...)):
    if bot_id not in bots:
        raise HTTPException(status_code=404, detail="Bot not found")
    # TODO: Implement scanning, analyzing, parsing, graph-based organization, and integration
    # For now, just acknowledge receipt
    file_names = [file.filename for file in files]
    return {"message": f"Received training files for bot {bot_id}: {file_names}"}

def run_orchestrator():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)

# Run orchestrator in a separate thread if needed
orchestrator_thread = threading.Thread(target=run_orchestrator, daemon=True)
orchestrator_thread.start()
