# 📌 Mini Chat en Temps Réel (FastAPI + React)

## 📂 Architecture du projet
```
📁 Trial Project Richard Portugais/
│── 📂 chat-app/          # Front-end React
│   │── src/              # Code source React
│   │── public/           # Fichiers statiques
│   │── package.json      # Dépendances front-end
│── 📄 server.py          # Back-end FastAPI (WebSockets + API REST)
│── 📄 chat.db            # Base de données SQLite
│── 📄 README.md          # Documentation
```

## 🚀 Installation & Exécution

### 1️⃣ Prérequis
- **Python** ≥ 3.8
- **Node.js** ≥ 16

### 2️⃣ Installer les dépendances
#### Back-end (Python + FastAPI)
```bash
pip install fastapi uvicorn sqlite3
```
#### Front-end (React.js)
```bash
cd chat-app
npm install
```

### 3️⃣ Lancer l’application
#### 1. Démarrer le serveur FastAPI
```bash
uvicorn server:app --reload
```
Le back-end est accessible sur **http://127.0.0.1:8000**.

#### 2. Démarrer le front-end React
Dans un **autre terminal** :
```bash
cd chat-app
npm start
```
Le chat est accessible sur **http://localhost:3000**.
