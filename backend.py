# backend.py (simplifié avec signaux simulés)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio, random, json
from fastapi.responses import HTMLResponse

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PAIRS = ["EUR/USD", "EUR/JPY", "USD/CAD", "EUR/CAD", "USD/JPY", "CAD/JPY"]
clients = []
data_state = {pair: 1.0 for pair in PAIRS}  # prix initial simulé

# Signaux simulés
async def fake_ticks():
    while True:
        for pair in PAIRS:
            prev = data_state[pair]
            price = round(prev + random.uniform(-0.005, 0.005), 4)
            data_state[pair] = price
            direction = "UP" if price >= prev else "DOWN"
            for ws_client in clients:
                await ws_client.send_json({"pair": pair, "price": price, "direction": direction})
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fake_ticks())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

# Frontend HTML
html_content = '''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>CoBitcoin Interface</title>
<style>
body, html { margin:0; height:100%; font-family: Arial, sans-serif; }
.container { display:flex; height:100vh; }
.quotex { flex:2; border-right:1px solid #ccc; }
.interface { flex:1; padding:10px; display:flex; flex-direction:column; }
#signal-cadre { height:100px; border:2px solid #333; margin-bottom:10px; display:flex; align-items:center; justify-content:center; font-size:24px; background:#f9f9f9; }
.paires button { width:100%; padding:10px; margin-bottom:5px; font-size:16px; }
</style>
</head>
<body>
<div class="container">
  <div class="quotex">
    <iframe id="quotex-frame" src="https://qxbroker.com/fr/sign-in" width="100%" height="100%" frameborder="0"></iframe>
  </div>
  <div class="interface">
    <div id="signal-cadre">Sélectionnez une paire</div>
    <div class="paires">
      <button onclick="selectPair('EUR/USD')">EUR/USD</button>
      <button onclick="selectPair('EUR/JPY')">EUR/JPY</button>
      <button onclick="selectPair('USD/CAD')">USD/CAD</button>
      <button onclick="selectPair('EUR/CAD')">EUR/CAD</button>
      <button onclick="selectPair('USD/JPY')">USD/JPY</button>
      <button onclick="selectPair('CAD/JPY')">CAD/JPY</button>
    </div>
  </div>
</div>
<script>
let currentPair = null;
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.pair === currentPair && data.direction) {
    document.getElementById('signal-cadre').textContent = `${data.pair} → ${data.direction}`;
    currentPair = null;
  }
};

function selectPair(pair) {
  currentPair = pair;
  document.getElementById('signal-cadre').textContent = `Analyse en cours pour ${pair}…`;
}
</script>
</body>
</html>'''

@app.get('/')
async def get_frontend():
    return HTMLResponse(content=html_content, status_code=200)
