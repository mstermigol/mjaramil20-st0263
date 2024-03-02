import json
import os

from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify

env_path = os.path.join(os.path.dirname(__file__), "./configs/.env_server")
load_dotenv(dotenv_path=env_path)

SERVER_URL = os.getenv("SERVER_URL")
SERVER_PORT = os.getenv("SERVER_PORT")

app = Flask(__name__)

@app.route("/upload", methods=["GET"])
def upload():
    pserver_data = request.json
    file_name = pserver_data.get("file_name")
    url = pserver_data.get("url")
    
    return Response(status=200)
    
    
if __name__ == "__main__":
    app.run(host=SERVER_URL, port=SERVER_PORT, debug=True)