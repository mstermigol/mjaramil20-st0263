import json
import os

from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify

env_path = os.path.join(os.path.dirname(__file__), "./configs/.env_server")
load_dotenv(dotenv_path=env_path)

SERVER_URL = os.getenv("SERVER_URL")
SERVER_PORT = os.getenv("SERVER_PORT")

app = Flask(__name__)

users = {}
files = {}
urls = {}
activeUsers = []

@app.route("/login", methods=["POST"])
def login():
    pserverData = request.json
    username = pserverData.get("username")
    password = pserverData.get("password")
    url = pserverData.get("url")
    if username in users:
        if users[username] == password:
            print(users)
            print(urls)
            print(activeUsers)
            return Response(status=200)
        else:
            return Response(status=401)
    else:
        users[username] = password
        urls[username] = url
        activeUsers.append(username)
        print(users)
        print(urls)
        print(activeUsers)
        return Response(status=200)


@app.route("/upload", methods=["GET"])
def upload():
    pserverData = request.json
    file_name = pserverData.get("file_name")
    url = pserverData.get("url")
    
    return Response(status=200)
    
    
if __name__ == "__main__":
    app.run(host=SERVER_URL, port=SERVER_PORT, debug=True)