import React, { useState, useEffect } from "react";

const App = () => {
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState("");
    const [username, setUsername] = useState("");
    const [ws, setWs] = useState(null);

    useEffect(() => {
        const websocket = new WebSocket("ws://localhost:8000/ws");

        websocket.onmessage = (event) => {
            const newMessage = JSON.parse(event.data);
            setMessages((prev) => [...prev, newMessage]);
        };

        setWs(websocket);

        fetch("http://localhost:8000/messages")
          .then((res) => res.json())
          .then((data) => setMessages(data.reverse()))
          .catch((error) => console.error("Erreur lors de la récupération des messages :", error));


        return () => websocket.close();
    }, []);

    const sendMessage = () => {
        if (message.trim() !== "" && username.trim() !== "") {
            const msg = { username, content: message };
            ws.send(JSON.stringify(msg));
            setMessage("");
        }
    };

    return (
        <div style={{ maxWidth: "600px", margin: "auto", padding: "20px", textAlign: "center" }}>
            <h2>Chat en Temps Réel</h2>
            <input
                type="text"
                placeholder="Votre pseudo"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={{ marginBottom: "10px", padding: "5px", width: "100%" }}
            />
            <div
                style={{
                    border: "1px solid black",
                    height: "300px",
                    overflowY: "auto",
                    padding: "10px",
                    marginBottom: "10px",
                    backgroundColor: "#f9f9f9",
                }}
            >
                {messages.map((msg, index) => (
                    <div key={index}>
                        <b>{msg.username}</b>: {msg.content}
                    </div>
                ))}
            </div>
            <input
                type="text"
                placeholder="Votre message..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                style={{ width: "80%", padding: "5px" }}
            />
            <button onClick={sendMessage} style={{ marginLeft: "10px", padding: "5px 10px" }}>
                Envoyer
            </button>
        </div>
    );
};

export default App;
