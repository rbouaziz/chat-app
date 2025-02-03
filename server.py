from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List
import sqlite3
import json

app = FastAPI()

# Connexion SQLite
conn = sqlite3.connect("chat.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        content TEXT,
        timestamp TEXT
    )
""")
conn.commit()

# Stockage des connexions WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            username = message.get("username")
            content = message.get("content")

            # Stocker le message dans SQLite
            cursor.execute("INSERT INTO messages (username, content, timestamp) VALUES (?, ?, datetime('now'))",
                           (username, content))
            conn.commit()

            # Diffuser à tous les utilisateurs connectés
            await manager.broadcast(json.dumps({"username": username, "content": content}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/messages")
async def get_messages():
    cursor.execute("SELECT username, content, timestamp FROM messages ORDER BY id DESC LIMIT 50")
    messages = cursor.fetchall()
    return JSONResponse([{"username": m[0], "content": m[1], "timestamp": m[2]} for m in messages])

@app.post("/messages")
async def post_message(data: dict):
    username = data.get("username")
    content = data.get("content")

    if not username or not content:
        return JSONResponse({"error": "Username and content required"}, status_code=400)

    cursor.execute("INSERT INTO messages (username, content, timestamp) VALUES (?, ?, datetime('now'))",
                   (username, content))
    conn.commit()

    await manager.broadcast(json.dumps({"username": username, "content": content}))
    return JSONResponse({"message": "Message sent"})
