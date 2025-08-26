# main.py
import os
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse   # ← FileResponseを追加！

app = FastAPI()

# 静的ファイル配信（index.html等）
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS（必要なら調整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 接続クライアント管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # サーバー側で保持する現在の色（初期値）
        self.current_color = "#ffffff"

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # 接続したクライアントに現在の色を送る
        await websocket.send_text(json.dumps({"type": "set_color", "color": self.current_color}))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # 全クライアントに送信（例外により切断された接続は除去）
        disconnected = []
        for ws in list(self.active_connections):
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

manager = ConnectionManager()

@app.get("/")
async def root():
    # static/index.html を返す
    return FileResponse(os.path.join("static", "index.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    websocket protocol:
    - クライアント -> サーバ:
      {"type":"change_color", "color":"#ff0000"}
    - サーバ -> クライアント:
      {"type":"set_color", "color":"#ff0000"}
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except Exception:
                # 無効なJSONは無視
                continue

            if payload.get("type") == "change_color":
                color = payload.get("color")
                if isinstance(color, str) and color.startswith("#") and (len(color) in (4,7)):
                    # サーバ側の状態更新
                    manager.current_color = color
                    # ブロードキャスト
                    await manager.broadcast(json.dumps({"type": "set_color", "color": color}))
                else:
                    # 無効な色は無視（必要ならエラー応答を送る）
                    pass
            # 他のメッセージタイプがあればここに
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
