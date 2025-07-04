
from flask import Flask, Response, render_template
import time

app = Flask(__name__)

LOG_FILE = "../ai/event_log.log"

@app.route('/')
def index():
    return render_template('log_viewer.html')

@app.route('/stream')
def stream():
    def event_stream():
        with open(LOG_FILE, "r") as f:
            f.seek(0, 2)  # Move to end of file
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line}\n\n"
                else:
                    time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True, port=5002, host="0.0.0.0")
