import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# Renderが提供するポート番号を環境変数から取得します。
port = int(os.environ.get('PORT', 5000))
# セキュリティのためにシークレットキーを環境変数から取得します
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret') 
socketio = SocketIO(app, cors_allowed_origins="*")

# トップページにアクセスされたときにindex.htmlをレンダリングします
@app.route('/')
def index():
    return render_template('index.html')

# クライアントが接続したときに実行されます
@socketio.on('connect')
def test_connect():
    print('Client connected')
    emit('my response', {'data': 'Connected'})

# クライアントが切断したときに実行されます
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

# クライアントから'change_color'というイベントを受信したときに実行されます
@socketio.on('change_color')
def handle_color_change(json_data):
    print('received message: ' + str(json_data))
    # 'broadcast=True'で接続中のすべてのクライアントにイベントを送信します
    emit('update_color', json_data, broadcast=True) 