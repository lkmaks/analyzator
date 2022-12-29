from app import app, socketio
import os


port = 5555

is_local = os.environ.get('LOCAL')

if not is_local:
    port = os.environ['PORT']

socketio.run(app, host='0.0.0.0', port=port, debug=False)



