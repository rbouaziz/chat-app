from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List
import sqlite3
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines (à sécuriser en prod)
    allow_credentials=True,
    allow_methods=["*"],  # Autoriser toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Autoriser tous les headers
)


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
            try:
                message = json.loads(data)
                username = message.get("username")
                content = message.get("content")

                # Vérification du format
                if not username or not content:
                    await websocket.send_text(json.dumps({"error": "Le message doit contenir un 'username' et un 'content'"}))
                    continue  # Ignore ce message mal formaté

                # Stocker le message dans la base de données
                cursor.execute("INSERT INTO messages (username, content, timestamp) VALUES (?, ?, datetime('now'))",
                               (username, content))
                conn.commit()

                # Diffuser le message à tous les utilisateurs connectés
                await manager.broadcast(json.dumps({"username": username, "content": content}))

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Format JSON invalide"}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/messages")
async def get_messages():
    cursor.execute("SELECT username, content, timestamp FROM messages ORDER BY id DESC LIMIT 50")
    messages = cursor.fetchall()
    return JSONResponse([{"username": m[0], "content": m[1], "timestamp": m[2]} for m in messages])

@app.post("/messages")
async def post_message(data: dict):
    try:
        username = data.get("username")
        content = data.get("content")

        # Vérification des champs obligatoires
        if not username or not content:
            return JSONResponse({"error": "Le message doit contenir 'username' et 'content'"}, status_code=400)

        # Stocker dans la base de données
        cursor.execute("INSERT INTO messages (username, content, timestamp) VALUES (?, ?, datetime('now'))",
                       (username, content))
        conn.commit()

        # Diffuser à tous les utilisateurs connectés
        await manager.broadcast(json.dumps({"username": username, "content": content}))
        return JSONResponse({"message": "Message envoyé"})

    except Exception as e:
        return JSONResponse({"error": f"Erreur interne : {str(e)}"}, status_code=500)
