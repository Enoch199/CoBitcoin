# CoBitcoin WebApp - Backend + Frontend
# Backend: FastAPI + WebSocket for real-time forex signal (UP/DOWN)
# Frontend: HTML + JS, iframe for Quotex left, signal + 6 pairs right

# --------------------- Backend ---------------------
# File: backend.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import aiohttp
import os
import json

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("TWELVEDATA_API_KEY")  # Set your Twelve Data API key in environment variables
PAIRS = {
    "EUR/USD": "EURUSD",
    "EUR/JPY": "EURJPY",
    "USD/CAD": "USDCAD",
    "EUR/CAD": "EURCAD",
    "USD/JPY": "USDJPY",
    "CAD/JPY": "CADJPY"
}

clients = []
last_price = {pair: None for pair in PAIRS.keys()}

async def fetch_ticks():
    url = "wss://ws.twelvedata.com/v1/quotes/price"
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            symbols = ",".join(PAIRS.values())
            await ws.send_json({"action": "subscribe", "pairs": symbols, "apikey": API_KEY})
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    symbol = data.get("symbol")
                    price = data.get("price")
                    for k, v in PAIRS.items():
                        if v == symbol:
                            prev = last_price[k]
                            last_price[k] = price
                            if prev is not None:
                                direction = "UP" if price >= prev else "DOWN"
                            else:
                                direction = None
                            for ws_client in clients:
                                await ws_client.send_json({"pair": k, "price": price, "direction": direction})
                            break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_ticks())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

# --------------------- Frontend ---------------------
# File: index.html
html_content = '''
<!DOCTYPE html>
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
const ws = new WebSocket("ws://localhost:8000/ws"); // Update URL if deployed

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.pair === currentPair && data.direction) {
    document.getElementById('signal-cadre').textContent = `${data.pair} → ${data.direction}`;
    currentPair = null; // signal affiché, attend prochaine sélection
  }
};

function selectPair(pair) {
  currentPair = pair;
  const iframe = document.getElementById('quotex-frame');
  iframe.src = `https://qxbroker.com/fr/sign-in?pair=${encodeURIComponent(pair)}`;
  document.getElementById('signal-cadre').textContent = `Analyse en cours pour ${pair}…`;
}
</script>
</body>
</html>
'''

# Optionally, serve frontend via FastAPI
from fastapi.responses import HTMLResponse
@app.get('/')
async def get_frontend():
    return HTMLResponse(content=html_content, status_code=200)

# --------------------- Deployment ---------------------
# Run: uvicorn backend:app --reload
# Set environment variable: export TWELVEDATA_API_KEY=your_api_key
