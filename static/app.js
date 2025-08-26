// app.js
(() => {
  const wsProtocol = (location.protocol === "https:") ? "wss" : "ws";
  // WebSocketエンドポイント（同一ホスト）
  const wsUrl = `${wsProtocol}://${location.host}/ws`;
  const socket = new WebSocket(wsUrl);

  const colorPicker = document.getElementById("colorPicker");
  const sendBtn = document.getElementById("sendBtn");
  const randomBtn = document.getElementById("randomBtn");
  const statusEl = document.getElementById("status");

  function setBg(color) {
    document.documentElement.style.setProperty("--bg", color);
    colorPicker.value = color;
  }

  function randomColor() {
    const r = Math.floor(Math.random()*256).toString(16).padStart(2,'0');
    const g = Math.floor(Math.random()*256).toString(16).padStart(2,'0');
    const b = Math.floor(Math.random()*256).toString(16).padStart(2,'0');
    return `#${r}${g}${b}`;
  }

  socket.addEventListener("open", () => {
    statusEl.textContent = "接続中";
  });

  socket.addEventListener("close", () => {
    statusEl.textContent = "切断";
  });

  socket.addEventListener("error", () => {
    statusEl.textContent = "エラー";
  });

  socket.addEventListener("message", (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      if (msg.type === "set_color" && typeof msg.color === "string") {
        setBg(msg.color);
      }
    } catch (e) {
      console.error("invalid message", e);
    }
  });

  function sendColor(color) {
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({type: "change_color", color}));
    } else {
      alert("サーバーに接続されていません。");
    }
  }

  sendBtn.addEventListener("click", () => {
    sendColor(colorPicker.value);
  });

  randomBtn.addEventListener("click", () => {
    const c = randomColor();
    sendColor(c);
  });

  // 色ピッカー変更でローカルだけ色を変える（押下で全端末に送る方針）
  colorPicker.addEventListener("input", (e) => {
    setBg(e.target.value);
  });
})();
