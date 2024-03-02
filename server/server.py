import json
import os
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify
import time
from datetime import datetime

env_path = os.path.join(os.path.dirname(__file__), "./configs/.env_server")
load_dotenv(dotenv_path=env_path)

SERVER_URL = os.getenv("SERVER_URL")
SERVER_PORT = os.getenv("SERVER_PORT")

app = Flask(__name__)

users = {}
files = {}
urls = {}
activeUsers = {}

@app.route("/login", methods=["POST"])
def login():
    pserverData = request.json
    username = pserverData.get("username")
    password = pserverData.get("password")
    url = pserverData.get("url")
    lastPing = pserverData.get("lastPing")
    if username in users:
        if users[username] == password:
            activeUsers[username] = lastPing
            return Response(status=200)
        else:
            return Response(status=401)
    else:
        users[username] = password
        urls[username] = url
        activeUsers[username] = lastPing
        return Response(status=200)


@app.route("/upload", methods=["GET"])
def upload():
    pserverData = request.json
    file_name = pserverData.get("file_name")
    url = pserverData.get("url")
    
    return Response(status=200)
    

@app.route("/ping", methods=["POST"])
def Ping():
    pserverData = request.json
    username = pserverData.get("username")
    lastPing = pserverData.get("lastPing")
    activeUsers[username] = lastPing
    return Response(status=200)

def CheckPings():
    while True:
        currentTime = datetime.now()
        usersRemove = []
        if activeUsers:
            for username, lastPing in activeUsers.items():
                if (currentTime - datetime.strptime(lastPing, "%Y-%m-%d %H:%M:%S")).total_seconds() > 10:
                    usersRemove.append(username)
            for username in usersRemove:
                print(f"{username} deleted")
                
                del activeUsers[username]
        time.sleep(15)

if __name__ == "__main__":
    ping_checker_thread = Thread(target=CheckPings)
    ping_checker_thread.daemon = True
    ping_checker_thread.start()
    app.run(host=SERVER_URL, port=SERVER_PORT, debug=True)