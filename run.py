from app import app, socketio
import os

port = os.environ['PORT']
socketio.run(app, host='0.0.0.0', port=port, debug=False)

