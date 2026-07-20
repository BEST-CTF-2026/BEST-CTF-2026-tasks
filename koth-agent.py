from pathlib import Path

from flask import Flask, jsonify

app = Flask(__name__)

KING_FILE = Path("/root/king.txt")
LISTEN_PORT = 31337


@app.route("/king")
def king():
    try:
        content = KING_FILE.read_text().strip()
    except FileNotFoundError:
        content = ""
    return content, 200, {"Content-Type": "text/plain"}


@app.route("/healthcheck")
def healthcheck():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=LISTEN_PORT)
